from logging import ERROR, INFO, LogRecord, Logger, getLogger
from logging.handlers import QueueHandler
from queue import Queue
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.exceptions import RequestValidationError
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.threading import ThreadingIntegration

import lib.utils.sentry as sentry_module
from lib.api.lib import exception_handlers
from lib.utils.CustomLogger import AutoExcInfoQueueHandler, ExcInfoFilter


def _fake_settings(**overrides):
    values = {
        "env": "production",
        "sentry_dsn": "https://public@example.ingest.sentry.io/1",
        "version": "9.9.9",
        "sensitive_endpoints": {"/settings/ai/keys/openai"},
        "login_method": "cookies",
        "is_logged_in": False,
    }
    values.update(overrides)

    return SimpleNamespace(**values)


# ----------------------------------------------------------------------------
# init_sentry
# ----------------------------------------------------------------------------

def test_init_skipped_when_no_dsn():
    with patch.object(sentry_module, "settings", _fake_settings(sentry_dsn="  ")), \
         patch.object(sentry_module, "_running_under_pytest", return_value=False), \
         patch.object(sentry_module, "_sentry_initialized", False), \
         patch("lib.utils.sentry.sentry_sdk.init") as init:
        assert sentry_module.init_sentry() is False
        init.assert_not_called()


def test_init_skipped_in_test_env():
    with patch.object(sentry_module, "settings", _fake_settings(env="test")), \
         patch.object(sentry_module, "_running_under_pytest", return_value=False), \
         patch.object(sentry_module, "_sentry_initialized", False), \
         patch("lib.utils.sentry.sentry_sdk.init") as init:
        assert sentry_module.init_sentry() is False
        init.assert_not_called()


def test_init_skipped_under_pytest_even_with_dsn():
    with patch.object(sentry_module, "settings", _fake_settings()), \
         patch.object(sentry_module, "_sentry_initialized", False), \
         patch("lib.utils.sentry.sentry_sdk.init") as init:
        assert sentry_module.init_sentry() is False
        init.assert_not_called()


def test_init_configures_full_error_tracking():
    for env in ("development", "production"):
        with patch.object(sentry_module, "settings", _fake_settings(env=env)), \
             patch.object(sentry_module, "_running_under_pytest", return_value=False), \
             patch.object(sentry_module, "_sentry_initialized", False), \
             patch("lib.utils.sentry.sentry_sdk.init") as init:
            assert sentry_module.init_sentry() is True

            kwargs = init.call_args.kwargs
            assert kwargs["dsn"] == "https://public@example.ingest.sentry.io/1"
            assert kwargs["environment"] == env
            assert kwargs["release"] == "streamstorm-engine@9.9.9"
            assert kwargs["traces_sample_rate"] == 1.0
            assert "profile_session_sample_rate" not in kwargs
            assert "profiles_sample_rate" not in kwargs
            assert kwargs["attach_stacktrace"] is True
            assert kwargs["include_local_variables"] is True
            assert kwargs["send_default_pii"] is False
            assert kwargs["before_send"] is sentry_module._before_send

            integration_types = {type(i) for i in kwargs["integrations"]}
            assert integration_types == {
                FastApiIntegration,
                StarletteIntegration,
                AsyncioIntegration,
                ThreadingIntegration,
                LoggingIntegration,
            }


# ----------------------------------------------------------------------------
# before_send scrubbing
# ----------------------------------------------------------------------------

def test_before_send_strips_secrets_for_sensitive_endpoints():
    event = {
        "request": {
            "url": "http://127.0.0.1:1919/settings/ai/keys/openai",
            "data": {"api_key": "sk-secret"},
            "cookies": {"a": "b"},
        },
        "exception": {
            "values": [{"stacktrace": {"frames": [{"vars": {"data": "AIProviderKeyData(api_key='sk-secret')"}}]}}]
        },
    }

    with patch.object(sentry_module, "settings", _fake_settings()):
        result = sentry_module._before_send(event, {})

    assert "data" not in result["request"]
    assert "cookies" not in result["request"]
    assert "vars" not in result["exception"]["values"][0]["stacktrace"]["frames"][0]
    assert "sk-secret" not in str(result)


def test_before_send_adds_runtime_context_tags():
    with patch.object(sentry_module, "settings", _fake_settings()):
        result = sentry_module._before_send({"request": {"url": "http://x/storm/start"}}, {})

    assert {"os", "login_method", "is_logged_in", "storm_running", "engine_busy"} <= set(result["tags"])


def test_before_send_never_raises():
    with patch.object(sentry_module, "_add_runtime_context", side_effect=RuntimeError("boom")), \
         patch.object(sentry_module, "settings", _fake_settings()):
        assert sentry_module._before_send({}, {}) == {}


# ----------------------------------------------------------------------------
# ExcInfoFilter / AutoExcInfoQueueHandler
# ----------------------------------------------------------------------------

def _record(level: int = ERROR) -> LogRecord:
    return LogRecord("t", level, __file__, 1, "something failed", None, None)


def test_exc_info_filter_attaches_active_exception():
    record = _record()

    try:
        raise ValueError("kaboom")
    except ValueError:
        ExcInfoFilter().filter(record)

    assert record.exc_info is not None
    assert record.exc_info[0] is ValueError
    assert record.auto_exc_info is True


def test_exc_info_filter_ignores_non_error_and_no_active_exception():
    info_record = _record(INFO)
    try:
        raise ValueError("kaboom")
    except ValueError:
        ExcInfoFilter().filter(info_record)
    assert not info_record.exc_info

    error_record = _record()
    ExcInfoFilter().filter(error_record)
    assert not error_record.exc_info


def test_exc_info_filter_keeps_explicit_exc_info():
    record = _record()
    explicit = (KeyError, KeyError("x"), None)
    record.exc_info = explicit

    try:
        raise ValueError("other")
    except ValueError:
        ExcInfoFilter().filter(record)

    assert record.exc_info is explicit
    assert not getattr(record, "auto_exc_info", False)


def test_auto_exc_info_not_rendered_into_queued_message_but_kept_for_sentry():
    queue: Queue = Queue()
    handler = AutoExcInfoQueueHandler(queue)
    handler.addFilter(ExcInfoFilter())

    logger: Logger = getLogger("tests.sentry.auto_exc")
    logger.propagate = False
    logger.addHandler(handler)

    captured: list[LogRecord] = []

    class Spy(QueueHandler):
        def emit(self, record):  # runs after the filter, sees the original record
            captured.append(record)

    spy = Spy(Queue())
    spy.addFilter(ExcInfoFilter())
    logger.addHandler(spy)

    try:
        try:
            raise ValueError("kaboom")
        except ValueError:
            logger.error("handled failure")

        queued: LogRecord = queue.get_nowait()

        # Queued (file / UI) message keeps its original, traceback-free format
        assert queued.getMessage() == "handled failure"
        assert "Traceback" not in queued.getMessage()

        # The original record still carries exc_info for Sentry's LoggingIntegration
        assert captured and captured[0].exc_info is not None
    finally:
        logger.removeHandler(handler)
        logger.removeHandler(spy)


# ----------------------------------------------------------------------------
# Exception handlers report to Sentry
# ----------------------------------------------------------------------------

def run(coroutine):
    """Drive a coroutine that never actually suspends (the handlers have no awaits)."""
    try:
        coroutine.send(None)
    except StopIteration as stop:
        return stop.value
    raise AssertionError("handler unexpectedly suspended")


def test_all_exception_handlers_report_to_sentry():
    validation_error = RequestValidationError(
        [{"loc": ("body", "messages"), "msg": "Value error, bad messages", "type": "value_error"}]
    )

    cases = [
        (exception_handlers.common_exception_handler, RuntimeError("x"), "unexpected"),
        (exception_handlers.business_exception_handler, SystemError("x"), "business"),
        (exception_handlers.validation_exception_handler, validation_error, "validation"),
        (exception_handlers.session_not_created_exception_handler, RuntimeError("x"), "browser_session"),
    ]

    for handler, exc, kind in cases:
        with patch.object(exception_handlers, "capture_handled_exception") as capture:
            run(handler(None, exc))
            capture.assert_called_once_with(exc, kind)
