from logging import ERROR, INFO, Logger, getLogger
from platform import system
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

# Local-variable / payload keys that must never leave the user's machine.
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
]

_SENSITIVE_PATH_PREFIXES: tuple[str, ...] = ("/settings/ai/keys",)

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


def _strip_frame_variables(event: dict[str, Any]) -> None:
    for exception in (event.get("exception") or {}).get("values", []) or []:
        for frame in (exception.get("stacktrace") or {}).get("frames", []) or []:
            frame.pop("vars", None)


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
    """Scrub secrets and enrich events with runtime context. Must never raise."""
    try:
        if _is_sensitive_event(event):
            _strip_frame_variables(event)

            request: dict[str, Any] = event.get("request") or {}
            for key in ("data", "cookies", "query_string"):
                request.pop(key, None)

        _add_runtime_context(event)

    except Exception as e:  # noqa: BLE001
        logger.debug(f"Sentry before_send failed: {e}")

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
        traces_sample_rate=1.0,
        attach_stacktrace=True,
        include_local_variables=True,
        send_default_pii=False,
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
