from json import dumps, loads
from threading import Thread
from unittest.mock import MagicMock

from pytest import MonkeyPatch, raises

import lib.settings.Settings as settings_module
from lib.ai.PydanticAI import PydanticAI
from lib.settings.SavedSettings import AISettings, DEFAULT_SAVED_SETTINGS, SavedSettings


def _use_settings_file(monkeypatch: MonkeyPatch, tmp_path, content: str | None = None):
    path = tmp_path / "settings.json"
    monkeypatch.setattr(settings_module, "SETTINGS_FILE_PATH", path)
    monkeypatch.setattr(settings_module, "APP_DATA_DIR", tmp_path)

    if content is not None:
        path.write_text(content, encoding="utf-8")

    return path


def test_default_engine_is_chromium():
    assert SavedSettings().engine == "chromium"
    assert DEFAULT_SAVED_SETTINGS["engine"] == "chromium"


def test_missing_engine_key_migrates_to_chromium(monkeypatch, tmp_path):
    _use_settings_file(monkeypatch, tmp_path, dumps({"login_method": "cookies"}))

    assert settings_module.read_settings_json().engine == "chromium"


def test_legacy_browser_engine_values_migrate(monkeypatch, tmp_path):
    _use_settings_file(monkeypatch, tmp_path, dumps({"browser_engine": "native"}))
    assert settings_module.read_settings_json().engine == "chromium"

    _use_settings_file(monkeypatch, tmp_path, dumps({"browser_engine": "obscura"}))
    assert settings_module.read_settings_json().engine == "obscura"


def test_explicit_saved_obscura_is_kept(monkeypatch, tmp_path):
    _use_settings_file(monkeypatch, tmp_path, dumps({"engine": "obscura"}))

    assert settings_module.read_settings_json().engine == "obscura"


def test_invalid_engine_value_falls_back_without_losing_api_keys(monkeypatch, tmp_path):
    ai = AISettings()
    ai.providers.openai.apiKey = "sk-keep-me-12345"
    path = _use_settings_file(monkeypatch, tmp_path, dumps({"ai": ai.model_dump(), "engine": "firefox"}))

    result = settings_module.read_settings_json()

    assert result.engine == "chromium"
    assert result.ai.providers.openai.apiKey == "sk-keep-me-12345"
    assert (tmp_path / "settings.json.bak").exists()
    assert loads((tmp_path / "settings.json.bak").read_text())["engine"] == "firefox"
    assert path.exists()


def test_non_dict_settings_file_does_not_crash(monkeypatch, tmp_path):
    _use_settings_file(monkeypatch, tmp_path, "[1, 2, 3]")

    assert settings_module.read_settings_json().engine == "chromium"


def test_corrupt_json_is_recreated_with_defaults(monkeypatch, tmp_path):
    path = _use_settings_file(monkeypatch, tmp_path, "{not json")

    assert settings_module.read_settings_json().engine == "chromium"
    assert loads(path.read_text())["engine"] == "chromium"


def test_write_is_atomic_and_leaves_no_temp_file(monkeypatch, tmp_path):
    path = _use_settings_file(monkeypatch, tmp_path)

    settings_module.write_settings_json({"engine": "obscura", "login_method": "profiles"})

    assert loads(path.read_text()) == {"engine": "obscura", "login_method": "profiles"}
    assert not (tmp_path / "settings.json.tmp").exists()


def test_concurrent_reads_never_see_torn_file(monkeypatch, tmp_path):
    _use_settings_file(monkeypatch, tmp_path)
    settings_module.write_settings_json(SavedSettings().model_dump())
    failures: list[Exception] = []

    def writer():
        for i in range(100):
            settings_module.write_settings_json(
                {**SavedSettings().model_dump(), "engine": "obscura" if i % 2 else "chromium"}
            )

    def reader():
        for _ in range(100):
            try:
                assert settings_module.read_settings_json().engine in {"chromium", "obscura"}
            except Exception as e:  # noqa: BLE001
                failures.append(e)

    threads = [Thread(target=writer), Thread(target=reader), Thread(target=reader)]
    [t.start() for t in threads]
    [t.join() for t in threads]

    assert failures == []


def test_explicit_provider_without_model_uses_that_providers_model(monkeypatch):
    ai_settings = AISettings(defaultProvider="openai", defaultModel="gpt-4o")
    ai_settings.providers.google.apiKey = "test-google-key"
    ai_settings.providers.google.model = "gemini-2.5-flash"
    monkeypatch.setattr(settings_module.settings, "ai", ai_settings)

    get_model = MagicMock(return_value=MagicMock())
    monkeypatch.setattr("lib.ai.PydanticAI.ModelFactory.get_model", get_model)

    PydanticAI(provider_name="google")

    assert get_model.call_args.kwargs["model_name"] == "gemini-2.5-flash"


def test_explicit_provider_without_any_model_raises(monkeypatch):
    ai_settings = AISettings(defaultProvider="openai", defaultModel="gpt-4o")
    ai_settings.providers.google.apiKey = "test-google-key"
    monkeypatch.setattr(settings_module.settings, "ai", ai_settings)

    with raises(SystemError, match="Model for google is not configured"):
        PydanticAI(provider_name="google")


def test_binary_garbage_settings_file_is_backed_up_and_recreated(monkeypatch, tmp_path):
    path = _use_settings_file(monkeypatch, tmp_path)
    path.write_bytes(b"\xff\xfe\x00garbage")

    assert settings_module.read_settings_json().engine == "chromium"
    assert (tmp_path / "settings.json.bak").read_bytes() == b"\xff\xfe\x00garbage"
    assert loads(path.read_text())["engine"] == "chromium"


def test_corrupt_json_keeps_backup_of_original(monkeypatch, tmp_path):
    _use_settings_file(monkeypatch, tmp_path, "{not json")

    settings_module.read_settings_json()

    assert (tmp_path / "settings.json.bak").read_text() == "{not json"


def test_non_dict_settings_file_keeps_backup_of_original(monkeypatch, tmp_path):
    _use_settings_file(monkeypatch, tmp_path, "[1, 2, 3]")

    settings_module.read_settings_json()

    assert (tmp_path / "settings.json.bak").read_text() == "[1, 2, 3]"


def test_failed_write_keeps_original_and_removes_temp_file(monkeypatch, tmp_path):
    path = _use_settings_file(monkeypatch, tmp_path, dumps({"engine": "obscura"}))
    monkeypatch.setattr(settings_module, "replace", MagicMock(side_effect=OSError("disk full")))

    with raises(OSError):
        settings_module.write_settings_json({"engine": "chromium"})

    assert loads(path.read_text()) == {"engine": "obscura"}
    assert not (tmp_path / "settings.json.tmp").exists()


def test_transient_permission_error_on_replace_is_retried(monkeypatch, tmp_path):
    path = _use_settings_file(monkeypatch, tmp_path, dumps({}))
    real_replace = settings_module.replace
    calls: list[int] = []

    def flaky_replace(source, destination):
        calls.append(1)

        if len(calls) < 3:
            raise PermissionError("busy")

        real_replace(source, destination)

    monkeypatch.setattr(settings_module, "replace", flaky_replace)
    monkeypatch.setattr(settings_module, "sleep", lambda _: None)

    settings_module.write_settings_json({"engine": "obscura"})

    assert len(calls) == 3
    assert loads(path.read_text()) == {"engine": "obscura"}
    assert not (tmp_path / "settings.json.tmp").exists()


def test_persistent_permission_error_on_replace_raises_and_cleans_temp_file(monkeypatch, tmp_path):
    _use_settings_file(monkeypatch, tmp_path, dumps({"engine": "obscura"}))
    failing_replace = MagicMock(side_effect=PermissionError("busy"))
    monkeypatch.setattr(settings_module, "replace", failing_replace)
    monkeypatch.setattr(settings_module, "sleep", lambda _: None)

    with raises(PermissionError):
        settings_module.write_settings_json({"engine": "chromium"})

    assert failing_replace.call_count == 5
    assert not (tmp_path / "settings.json.tmp").exists()
