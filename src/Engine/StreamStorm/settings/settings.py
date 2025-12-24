from pathlib import Path
from os import makedirs
from os.path import exists
from platform import system
from json import JSONDecodeError, dumps, loads
from logging import Logger, getLogger

from platformdirs import user_data_dir
from aiofiles import open as aio_open
from pydantic import model_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from asyncer import syncify

from .SavedSettings import SavedSettings, AISettings, DEFAULT_SAVED_SETTINGS

ROOT: Path = Path(__file__).parent.parent.parent.parent.parent.resolve()
APP_DATA_DIR: Path = Path(user_data_dir("StreamStorm", "DarkGlance"))
SETTINGS_FILE_PATH: Path = APP_DATA_DIR / "settings.json"

logger: Logger = getLogger(f"fastapi.{__name__}")

async def ensure_settings_json_file() -> None:
    """Ensure the settings file and directory exist"""
    if not exists(APP_DATA_DIR):
        makedirs(APP_DATA_DIR, exist_ok=True)
        logger.info(f"Created settings directory: {APP_DATA_DIR}")

    if not exists(SETTINGS_FILE_PATH):
        async with aio_open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as file:
            await file.write(dumps(DEFAULT_SAVED_SETTINGS, indent=4))
        logger.info(f"Created default settings file: {SETTINGS_FILE_PATH}")


async def read_settings_json() -> SavedSettings:        
    await ensure_settings_json_file()

    try:
        async with aio_open(SETTINGS_FILE_PATH, "r", encoding="utf-8") as file:
            content = await file.read()
            settings = loads(content)

            # Ensure AI section exists
            if "ai" not in settings:
                settings["ai"] = DEFAULT_SAVED_SETTINGS["ai"]

            return SavedSettings(**settings)

    except (JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error reading settings file, recreating: {e}")

        async with aio_open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as file:
            await file.write(dumps(DEFAULT_SAVED_SETTINGS, indent=4))

        return SavedSettings(**DEFAULT_SAVED_SETTINGS) 


async def write_settings(settings: dict) -> None:
    """Write settings to file"""
    await ensure_settings_json_file()

    async with aio_open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as file:
        await file.write(dumps(settings, indent=4))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env", "../src/Engine/.env"),
        env_file_encoding="utf-8",
        env_prefix="STREAMSTORM_",
        validate_assignment=True
    )

    host: str = "0.0.0.0"
    port: int = 1919  # 1919, because 19 is the character number for "S" in the English alphabets.

    env: str = "development"  # Valid values {"development", "production", "test"}
    version: str = "3.5.2"
    root: Path = ROOT
    os: str = system()

    atatus_app_name: str = ""  # Fetches from env variable
    atatus_license_key: str = ""  # Fetches from env variable
    logfire_token: str = ""  # Fetches from env variable

    app_data_dir: Path = APP_DATA_DIR
    settings_file_path: Path = SETTINGS_FILE_PATH

    sensitive_endpoints: set[str] = {
        "/settings/ai/keys/anthropic",
        "/settings/ai/keys/google",
        "/settings/ai/keys/openai",
        "/settings/ai/default",
    }

    saved_settings: SavedSettings = Field(default_factory=SavedSettings) 
    ai: AISettings = Field(default_factory=AISettings)

    @model_validator(mode="before")
    @classmethod
    def load_saved_settings(cls, data: dict) -> dict:
        settings = syncify(read_settings_json, raise_sync_error=False)()
        data["saved_settings"] = settings
        data["ai"] = settings.ai

        return data

    @model_validator(mode="after")
    def save_settings(self) -> "Settings":
        settings_json_content: dict = self.saved_settings.model_dump()

        settings_json_content["ai"] = self.ai.model_dump()

        syncify(write_settings, raise_sync_error=False)(settings_json_content)  

        return self        


settings: Settings = Settings()

__all__: list[str] = ["settings"]

if __name__ == "__main__":
    print(settings.model_dump())
