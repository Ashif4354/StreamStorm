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
