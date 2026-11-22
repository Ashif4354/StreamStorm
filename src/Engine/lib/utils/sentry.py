from logging import ERROR, INFO, Logger, getLogger
from platform import system
from re import Pattern, compile as re_compile
from sys import modules
from typing import Any, Literal

import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.threading import ThreadingIntegration
from sentry_sdk.scrubber import DEFAULT_DENYLIST, EventScrubber

from ..settings import settings

logger: Logger = getLogger(f"streamstorm.{__name__}")

_sentry_initialized: bool = False

REDACTED: str = "[Filtered]"

_EXTRA_DENYLIST: list[str] = [
    "apiKey",
    "api_key",
    "cookies",
    "cookie",
    "all_cookies",
    "final_cookies",
    "parsed_cookies",
    "license_key",
    "logfire_token",
    "sentry_dsn",
    "content",
    "content_str",
    "parsed",
    "provider",
    "ai_settings",
]

_SENSITIVE_KEY_PARTS: tuple[str, ...] = (
    "apikey",
    "api_key",
    "cookie",
    "token",
    "secret",
    "password",
    "passwd",
    "authorization",
    "credential",
    "license_key",
    "sentry_dsn",
)

_SENSITIVE_KEY_EXACT: frozenset[str] = frozenset({"provider", "providers", "ai_settings"})

_SENSITIVE_KEY_PREFIXES: tuple[str, ...] = ("content", "parsed")

_VALUE_PATTERNS: tuple[tuple[Pattern[str], str], ...] = (
    (re_compile(r"\bsk-[A-Za-z0-9_\-]{8,}"), REDACTED),
    (re_compile(r"\bAIza[0-9A-Za-z_\-]{20,}"), REDACTED),
    (re_compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=\-]{8,}"), f"Bearer {REDACTED}"),
    (
        re_compile(
            r"(?i)((?:api[_-]?key|token|secret|password|passwd|authorization|cookies?)\w*[\"']?\s*[:=]\s*)([\"']?)[^\"'\s,)}\]]+"
        ),
        rf"\1\2{REDACTED}",
    ),
    (
        re_compile(
            r"(?m)^[^\t\n]+\t(?:TRUE|FALSE)\t[^\t\n]*\t(?:TRUE|FALSE)\t-?\d+\t[^\t\n]+\t[^\n]*$"
        ),
        f"{REDACTED} (cookie line)",
    ),
    (re_compile(r"(?i)([\"']value[\"']\s*:\s*[\"'])[^\"']{6,}([\"'])"), rf"\1{REDACTED}\2"),
    (
        re_compile(r"\b(__Secure-[0-9A-Za-z]+|SAPISID|APISID|HSID|SSID|SIDCC|SID|LOGIN_INFO)=[^;\s'\"]+"),
        rf"\1={REDACTED}",
    ),
)

_PATH_PATTERNS: tuple[tuple[Pattern[str], str], ...] = (
    (re_compile(r"(?i)([A-Za-z]:[\\/]+Users[\\/]+)[^\\/\s'\"]+"), r"\1[user]"),
    (re_compile(r"(/home/)[^/\s'\"]+"), r"\1[user]"),
    (re_compile(r"(/Users/)[^/\s'\"]+"), r"\1[user]"),
)

_VALIDATION_ERROR_TYPES: frozenset[str] = frozenset({"RequestValidationError", "ValidationError"})

_SENSITIVE_PATH_PREFIXES: tuple[str, ...] = ("/settings/ai/keys",)

_SOURCE_CONTEXT_KEYS: frozenset[str] = frozenset({"context_line", "pre_context", "post_context"})

_MAX_SCRUB_DEPTH: int = 40

ErrorKind = Literal["unexpected", "business", "validation", "browser_session"]


def _is_sensitive_event(event: dict[str, Any]) -> bool:
    """Return True if the event originates from an endpoint that handles secrets."""
    url: str = (event.get("request") or {}).get("url", "") or ""
    transaction: str = event.get("transaction", "") or ""

    paths: set[str] = set(settings.sensitive_endpoints)

    return any(
        path in url or path in transaction for path in paths
    ) or any(
        prefix in url or prefix in transaction for prefix in _SENSITIVE_PATH_PREFIXES
    )


def _iter_stacktrace_frames(event: dict[str, Any]) -> list[dict[str, Any]]:
    frames: list[dict[str, Any]] = []

    for section in ("exception", "threads"):
        for entry in (event.get(section) or {}).get("values", []) or []:
            frames.extend((entry.get("stacktrace") or {}).get("frames", []) or [])

    return frames


def _strip_frame_variables(event: dict[str, Any]) -> None:
    for frame in _iter_stacktrace_frames(event):
        frame.pop("vars", None)


def _is_sensitive_key(key: str) -> bool:
    lowered: str = key.lower()

    return (
        lowered in _SENSITIVE_KEY_EXACT
        or lowered.startswith(_SENSITIVE_KEY_PREFIXES)
        or any(part in lowered for part in _SENSITIVE_KEY_PARTS)
    )


def _scrub_string(value: str) -> str:
    for pattern, replacement in _VALUE_PATTERNS:
        value = pattern.sub(replacement, value)

    for pattern, replacement in _PATH_PATTERNS:
        value = pattern.sub(replacement, value)

    return value


def _scrub(value: Any, key: str | None = None, depth: int = 0) -> Any:
    if depth > _MAX_SCRUB_DEPTH or key in _SOURCE_CONTEXT_KEYS:
        return value

    if key is not None and isinstance(value, (str, bytes, dict, list, tuple)) and value and _is_sensitive_key(key):
        return REDACTED

    if isinstance(value, str):
        return _scrub_string(value)

    if isinstance(value, dict):
        return {k: _scrub(v, k if isinstance(k, str) else None, depth + 1) for k, v in value.items()}

    if isinstance(value, (list, tuple)):
        return [_scrub(item, None, depth + 1) for item in value]

    return value


def _sanitize_validation_errors(event: dict[str, Any]) -> None:
    for exception in (event.get("exception") or {}).get("values", []) or []:
        error_type: str = exception.get("type") or ""

        if error_type in _VALIDATION_ERROR_TYPES:
            exception["value"] = f"{error_type}: input validation failed"


def _add_runtime_context(event: dict[str, Any]) -> None:
    # Imported lazily to avoid circular imports at module load.
    from ..core.EngineContext import EngineContext
    from ..core.StreamStorm import StreamStorm

    tags: dict[str, Any] = event.setdefault("tags", {})

    tags["os"] = system()
    tags["login_method"] = settings.login_method
    tags["is_logged_in"] = settings.is_logged_in
    tags["storm_running"] = StreamStorm.ss_instance is not None
    tags["engine_busy"] = EngineContext.is_busy()


def _before_send(event: dict[str, Any], hint: dict[str, Any]) -> dict[str, Any] | None:
    """Scrub secrets and enrich events with runtime context. Fails closed on scrub errors."""
    try:
        if _is_sensitive_event(event):
            _strip_frame_variables(event)

            request: dict[str, Any] = event.get("request") or {}
            for key in ("data", "cookies", "query_string"):
                request.pop(key, None)

        _sanitize_validation_errors(event)
        event = _scrub(event)

    except Exception as e:  # noqa: BLE001
        logger.debug(f"Sentry scrubbing failed, dropping event: {e}")
        return None

    try:
        _add_runtime_context(event)

    except Exception as e:  # noqa: BLE001
        logger.debug(f"Sentry runtime context failed: {e}")

    return event


def _running_under_pytest() -> bool:
    return "pytest" in modules


def init_sentry() -> bool:
    """
    Initialise Sentry once. Returns True if Sentry is active.

    Skipped in the test environment or when no DSN is configured (e.g. open-source
    contributors running from source without a STREAMSTORM_SENTRY_DSN).
    """
    global _sentry_initialized

    if _sentry_initialized:
        return True

    dsn: str = settings.sentry_dsn.strip()

    if settings.env == "test" or _running_under_pytest() or not dsn:
        logger.debug("Sentry disabled (test environment, pytest run, or no DSN configured)")
        return False

    failed_request_status_codes: set[int] = set(range(400, 600))

    sentry_sdk.init(
        dsn=dsn,
        environment=settings.env,
        release=f"streamstorm-engine@{settings.version}",
        traces_sample_rate=settings.sentry_traces_sample_rate,
        server_name="",
        attach_stacktrace=True,
        include_local_variables=True,
        max_breadcrumbs=100,
        max_value_length=8192,
        event_scrubber=EventScrubber(
            denylist=DEFAULT_DENYLIST + _EXTRA_DENYLIST,
            recursive=True,
        ),
        before_send=_before_send,
        integrations=[
            FastApiIntegration(
                transaction_style="endpoint",
                failed_request_status_codes=failed_request_status_codes,
            ),
            StarletteIntegration(
                transaction_style="endpoint",
                failed_request_status_codes=failed_request_status_codes,
            ),
            AsyncioIntegration(),
            ThreadingIntegration(),
            LoggingIntegration(
                level=INFO,
                event_level=ERROR,
                capture_sentry_logs=True,
            ),
        ],
    )

    _sentry_initialized = True
    logger.debug("Sentry initialised")

    return True


def capture_handled_exception(exc: BaseException, kind: ErrorKind = "unexpected") -> None:
    """Report an exception that was handled (and turned into a response) by an exception handler."""
    try:
        with sentry_sdk.new_scope() as scope:
            scope.set_tag("error.type", kind)
            sentry_sdk.capture_exception(exc)

    except Exception as e:  # noqa: BLE001
        logger.debug(f"Failed to report exception to Sentry: {e}")


def flush_sentry(timeout: float = 2.0) -> None:
    """Flush pending events, e.g. before the process is killed."""
    if not _sentry_initialized:
        return

    try:
        sentry_sdk.flush(timeout=timeout)

    except Exception as e:  # noqa: BLE001
        logger.debug(f"Failed to flush Sentry: {e}")


__all__: list[str] = ["init_sentry", "flush_sentry", "capture_handled_exception"]
