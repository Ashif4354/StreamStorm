from json import JSONDecodeError, dumps, loads
from logging import Logger, getLogger
from os import makedirs
from os.path import exists, join
from typing import Optional

from aiofiles import open as aio_open
from platformdirs import user_data_dir
from pydantic import BaseModel, Field

from ..settings import settings

logger: Logger = getLogger(f"fastapi.{__name__}")

APP_DATA_DIR: str = str(settings.app_data_dir)
SETTINGS_FILE_PATH: str = str(settings.settings_file_path)

# Default settings structure
"""
DEFAULT_SETTINGS: dict = {
    "ai": {
        "providers": {
            "openai": {
                "apiKey": "",
                "model": "",
                "baseUrl": "https://api.openai.com/v1",
            },
            "anthropic": {"apiKey": "", "model": "", "baseUrl": None},
            "google": {"apiKey": "", "model": "", "baseUrl": None},
        },
        "defaultProvider": None,
        "defaultModel": None,
        "defaultBaseUrl": None,
    }
}
"""


class Provider(BaseModel):
    apiKey: str = ""
    model: str = ""
    baseUrl: Optional[str] = None


# 2. Group them (The Chunin level)
class AIProviders(BaseModel):
    openai: Provider = Field(
        default_factory=lambda: Provider(baseUrl="https://api.openai.com/v1")
    )
    anthropic: Provider = Field(default_factory=Provider)
    google: Provider = Field(default_factory=Provider)


# 3. The Top Level (The Hokage level)
class AISettings(BaseModel):
    providers: AIProviders = Field(default_factory=AIProviders)
    defaultProvider: Optional[str] = None
    defaultModel: Optional[str] = None
    defaultBaseUrl: Optional[str] = None


class Settings(BaseModel):
    ai: AISettings = Field(default_factory=AISettings)


DEFAULT_SETTINGS: dict = Settings().model_dump()


async def ensure_settings_file() -> None:
    """Ensure the settings file and directory exist"""
    if not exists(APP_DATA_DIR):
        makedirs(APP_DATA_DIR, exist_ok=True)
        logger.info(f"Created settings directory: {APP_DATA_DIR}")

    if not exists(SETTINGS_FILE_PATH):
        async with aio_open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as file:
            await file.write(dumps(DEFAULT_SETTINGS, indent=4))
        logger.info(f"Created default settings file: {SETTINGS_FILE_PATH}")


async def read_settings(model_format: bool = False) -> dict | Settings:
    """Read settings from file, create if not exists"""
    await ensure_settings_file()

    try:
        async with aio_open(SETTINGS_FILE_PATH, "r", encoding="utf-8") as file:
            content = await file.read()
            settings = loads(content)

            # Ensure AI section exists
            if "ai" not in settings:
                settings["ai"] = DEFAULT_SETTINGS["ai"]

            if model_format:
                return Settings(**settings)

            return settings

    except (JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error reading settings file, recreating: {e}")
        async with aio_open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as file:
            await file.write(dumps(DEFAULT_SETTINGS, indent=4))

        if model_format:
            return Settings(**DEFAULT_SETTINGS)

        return DEFAULT_SETTINGS.copy()

    


async def write_settings(settings: dict) -> None:
    """Write settings to file"""
    await ensure_settings_file()

    async with aio_open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as file:
        await file.write(dumps(settings, indent=4))

__all__ = [
    "read_settings",
    "write_settings",
    "Settings",
]