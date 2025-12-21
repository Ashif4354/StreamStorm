from pathlib import Path
from platform import system

from platformdirs import user_data_dir

ROOT: Path = Path(__file__).parent.parent.parent.parent.parent.resolve()

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env", "../src/Engine/.env"),
        env_file_encoding="utf-8",
        env_prefix="STREAMSTORM_",
    )

    host: str = "0.0.0.0"
    port: int = 1919  # 1919, because 19 is the character number for "S" in the English alphabets.

    env: str = "development"  # Possible values {"development", "production", "test"}
    version: str = "3.5.2"
    root: Path = ROOT
    os: str = system()

    atatus_app_name: str = ""
    atatus_license_key: str = ""
    logfire_token: str = ""

    app_data_dir: Path = Path(user_data_dir("StreamStorm", "DarkGlance"))
    settings_file_path: Path = app_data_dir / "settings.json"

    sensitive_endpoints: set[str] = {
        "/settings/ai/keys/anthropic",
        "/settings/ai/keys/google",
        "/settings/ai/keys/openai",
        "/settings/ai/default",
    }


settings = Settings()

__all__: list[str] = ["settings"]

if __name__ == "__main__":
    print(settings.model_dump())
