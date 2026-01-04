from pathlib import Path
from os import makedirs
from os.path import exists
from platform import system
from json import JSONDecodeError, dumps, loads
from logging import Logger, getLogger
from typing import Literal

from platformdirs import user_data_dir
from pydantic import model_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .SavedSettings import SavedSettings, AISettings, DEFAULT_SAVED_SETTINGS

ROOT: Path = Path(__file__).parent.parent.parent.parent.parent.resolve()
APP_DATA_DIR: Path = Path(user_data_dir("StreamStorm", "DarkGlance"))
SETTINGS_FILE_PATH: Path = APP_DATA_DIR / "settings.json"

logger: Logger = getLogger(f"fastapi.{__name__}")

def ensure_settings_json_file() -> None:
    """Ensure the settings file and directory exist"""
    if not exists(APP_DATA_DIR):
        makedirs(APP_DATA_DIR, exist_ok=True)
        logger.info(f"Created settings directory: {APP_DATA_DIR}")

    if not exists(SETTINGS_FILE_PATH):
        with open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as file:
            file.write(dumps(DEFAULT_SAVED_SETTINGS, indent=4))
        logger.info(f"Created default settings file: {SETTINGS_FILE_PATH}")


def read_settings_json() -> SavedSettings:        
    ensure_settings_json_file()

    try:
        with open(SETTINGS_FILE_PATH, "r", encoding="utf-8") as file:
            content = file.read()
            settings = loads(content)

            # Ensure AI section exists
            if "ai" not in settings:
                settings["ai"] = DEFAULT_SAVED_SETTINGS["ai"]

            return SavedSettings(**settings)

    except (JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error reading settings file, recreating: {e}")

        with open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as file:
            file.write(dumps(DEFAULT_SAVED_SETTINGS, indent=4))

        return SavedSettings(**DEFAULT_SAVED_SETTINGS) 


def write_settings_json(settings: dict) -> None:
    """Write settings to file"""
    ensure_settings_json_file()

    with open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as file:
        file.write(dumps(settings, indent=4))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env", "../src/Engine/.env"),
        env_file_encoding="utf-8",
        env_prefix="STREAMSTORM_",
        validate_assignment=True
    )

    host: str = "0.0.0.0"
    port: int = 1919  # 1919, because 19 is the character number for "S" in the English alphabets.

    env: str = "production"  # Valid values {"development", "production", "test"}
    version: str = "3.5.2"
    root: Path = ROOT
    os: str = system()
    run_only_api: bool = False

    atatus_app_name: str = ""  # Fetches from env variable
    atatus_license_key: str = ""  # Fetches from env variable
    logfire_token: str = ""  # Fetches from env variable

    app_data_dir: Path = APP_DATA_DIR
    settings_file_path: Path = SETTINGS_FILE_PATH
    environment_dir: Path = APP_DATA_DIR / "Environment"
    data_json_path: Path = environment_dir / "data.json"
    cookies_path: Path = environment_dir / "cookies.json"
    log_file_path: str = "" # Will be set by CustomLogger during logging setup

    login_method: Literal["cookies", "profiles"] = "cookies"

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

    @model_validator(mode="before")
    @classmethod
    def load_saved_settings(cls, data: dict) -> dict:
        settings = read_settings_json()
        data["saved_settings"] = settings
        data["ai"] = settings.ai
        data["login_method"] = settings.login_method

        return data

    @model_validator(mode="after")
    def save_settings(self) -> "Settings":
        settings_json_content: dict = self.saved_settings.model_dump()

        settings_json_content["ai"] = self.ai.model_dump()
        settings_json_content["login_method"] = self.login_method

        write_settings_json(settings_json_content)  

        return self        


settings: Settings = Settings()

__all__: list[str] = ["settings"]

if __name__ == "__main__":
    print(settings.model_dump_json(indent=4))
