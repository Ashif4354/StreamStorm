import sys
from contextlib import suppress
from pathlib import Path
from os import makedirs, replace
from os.path import exists
from platform import system
from json import JSONDecodeError, dumps, loads
from logging import Logger, getLogger
from shutil import copyfile
from threading import RLock
from typing import Any, Literal

from platformdirs import user_data_dir
from pydantic import model_validator, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from .SavedSettings import SavedSettings, AISettings, DEFAULT_SAVED_SETTINGS

ROOT: Path = Path(__file__).parent.parent.parent.parent.parent.resolve()
APP_DATA_DIR: Path = Path(user_data_dir("StreamStorm", "DarkGlance"))
SETTINGS_FILE_PATH: Path = APP_DATA_DIR / "settings.json"

logger: Logger = getLogger(f"fastapi.{__name__}")
# Does not have a handler, so it will not log anything

_settings_file_lock: RLock = RLock()

def _write_file_atomically(path: Path, content: str) -> None:
    temp_path: Path = path.with_name(f"{path.name}.tmp")

    with open(temp_path, "w", encoding="utf-8") as file:
        file.write(content)

    replace(temp_path, path)


def ensure_settings_json_file() -> None:
    """Ensure the settings file and directory exist"""
    with _settings_file_lock:
        if not exists(APP_DATA_DIR):
            makedirs(APP_DATA_DIR, exist_ok=True)
            logger.info(f"Created settings directory: {APP_DATA_DIR}")

        if not exists(SETTINGS_FILE_PATH):
            _write_file_atomically(SETTINGS_FILE_PATH, dumps(DEFAULT_SAVED_SETTINGS, indent=4))
            logger.info(f"Created default settings file: {SETTINGS_FILE_PATH}")


def _migrate_loaded_settings(loaded: dict) -> dict:
    if "ai" not in loaded:
        loaded["ai"] = DEFAULT_SAVED_SETTINGS["ai"]

    if "login_method" not in loaded:
        loaded["login_method"] = "cookies"

    if "engine" not in loaded:
        loaded["engine"] = loaded.get("browser_engine", "chromium")

    if loaded["engine"] == "native":
        loaded["engine"] = "chromium"

    return loaded


def _recover_invalid_settings(loaded: dict, error: ValidationError) -> SavedSettings:
    invalid_fields: set[Any] = {err["loc"][0] for err in error.errors() if err["loc"]}
    logger.error(f"Invalid saved settings fields, falling back to defaults for: {sorted(map(str, invalid_fields))}")

    with suppress(OSError):
        copyfile(SETTINGS_FILE_PATH, SETTINGS_FILE_PATH.with_name(f"{SETTINGS_FILE_PATH.name}.bak"))

    try:
        return SavedSettings(**{k: v for k, v in loaded.items() if k not in invalid_fields})

    except ValidationError:
        return SavedSettings(**DEFAULT_SAVED_SETTINGS)


def read_settings_json() -> SavedSettings:
    with _settings_file_lock:
        ensure_settings_json_file()

        try:
            with open(SETTINGS_FILE_PATH, "r", encoding="utf-8") as file:
                loaded = loads(file.read())

        except (JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error reading settings file, recreating: {e}")

            _write_file_atomically(SETTINGS_FILE_PATH, dumps(DEFAULT_SAVED_SETTINGS, indent=4))

            return SavedSettings(**DEFAULT_SAVED_SETTINGS)

        if not isinstance(loaded, dict):
            loaded = {}

        loaded = _migrate_loaded_settings(loaded)

        try:
            return SavedSettings(**loaded)

        except ValidationError as e:
            return _recover_invalid_settings(loaded, e)


def write_settings_json(settings_dict: dict) -> None:
    """Write settings to file"""
    with _settings_file_lock:
        ensure_settings_json_file()
        _write_file_atomically(SETTINGS_FILE_PATH, dumps(settings_dict, indent=4))


_ENV_FILES: list[str | Path] = [".env", "../../.env", "../src/Engine/.env"]

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    # In the PyInstaller executable, a build-time env file (containing only the Sentry DSN)
    # is bundled inside the extracted bundle. It is placed first so any local .env overrides it.
    _ENV_FILES.insert(0, Path(sys._MEIPASS) / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=tuple(_ENV_FILES),
        env_file_encoding="utf-8",
        env_prefix="STREAMSTORM_",
        validate_assignment=True
    )

    host: str = "0.0.0.0"
    port: int = 1919  # 1919, because 19 is the character number for "S" in the English alphabets.

    env: str = "production"  # Valid values {"development", "production", "test"}
    version: str = "4.2.0"
    root: Path = ROOT
    os: str = system()
    run_only_api: bool = False

    sentry_dsn: str = ""  # Fetches from STREAMSTORM_SENTRY_DSN env variable. Empty disables Sentry.
    sentry_traces_sample_rate: float = Field(default=0.1, ge=0.0, le=1.0)
    logfire_token: str = "logfire_token"  # Fetches from env variable

    app_data_dir: Path = APP_DATA_DIR
    settings_file_path: Path = SETTINGS_FILE_PATH
    environment_dir: Path = APP_DATA_DIR / "Environment"
    screenshot_dir: Path = APP_DATA_DIR / "Screenshots"
    data_json_path: Path = environment_dir / "data.json"
    cookies_path: Path = environment_dir / "cookies.json"
    log_file_path: str = "" # Will be set by CustomLogger during logging setup

    login_method: Literal["cookies", "profiles"] = "cookies"
    engine: Literal["chromium", "obscura"] = "chromium"

    _initialized: bool = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, "_initialized", True)

    @property
    def is_logged_in(self) -> bool:
        """Check if user is logged in (both cookies.json and data.json exist)."""
        return exists(self.cookies_path) and exists(self.data_json_path)

    sensitive_endpoints: set[str] = {
        "/settings/ai/keys/anthropic",
        "/settings/ai/keys/google",
        "/settings/ai/keys/openai",
        "/settings/ai/default",
    }

    storm_controls_endpoints: set[str] = {
        "/storm/pause",
        "/storm/resume",
        "/storm/change_messages",
        "/storm/start_storm_dont_wait",
        "/storm/change_slow_mode",
        "/storm/start_more_channels",
        "/storm/kill_instance",
        "/storm/context",
    }

    busy_endpoints: set[str] = {
        "/storm/start",
        "/environment/profiles/create",
        "/environment/profiles/delete",
        "/channels/create",
        "/environment/profiles/add_account",
    }

    storm_control_tools: set[str] = {
        "pause_storm",
        "resume_storm",
        "change_storm_messages",
        "start_storm_dont_wait",
        "change_slow_mode",
        "add_channels_to_storm",
        "kill_instance",
        "get_storm_context",
    }

    busy_tools: set[str] = {
        "start_storm",
        "create_chromium_profiles",
        "delete_chromium_profiles",
    }

    cors_headers: dict[str, str] = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Headers": "*",
    }

    saved_settings: SavedSettings = Field(default_factory=SavedSettings) 
    ai: AISettings = Field(default_factory=AISettings)

    def save(self) -> None:
        """Write current persistent settings to settings.json"""
        settings_json_content: dict = self.saved_settings.model_dump()
        settings_json_content["ai"] = self.ai.model_dump()
        settings_json_content["login_method"] = self.login_method
        settings_json_content["engine"] = self.engine
        write_settings_json(settings_json_content)

    @model_validator(mode="before")
    @classmethod
    def load_saved_settings(cls, data: dict) -> dict:
        loaded = read_settings_json()
        data["saved_settings"] = loaded
        data["ai"] = loaded.ai
        data["login_method"] = loaded.login_method
        data["engine"] = loaded.engine

        return data

    @model_validator(mode="after")
    def save_settings(self) -> "Settings":
        self.save()
        return self

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)
        if getattr(self, "_initialized", False) and name in {"login_method", "engine", "ai"}:
            self.save()


settings: Settings = Settings()

__all__: list[str] = ["settings"]

if __name__ == "__main__":
    print(settings.model_dump_json(indent=4))
