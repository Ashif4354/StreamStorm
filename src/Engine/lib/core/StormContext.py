from json import load, JSONDecodeError 
from typing import Any, Literal
from logging import getLogger, Logger
from datetime import datetime 

from pydantic import BaseModel, model_validator, Field

from ..settings import settings

logger: Logger = getLogger(f"streamstorm.{__name__}")

def read_data_json() -> dict:
    try:
        with open(settings.data_json_path, "r", encoding="utf-8") as file:
            return load(file)
    except (FileNotFoundError, PermissionError, UnicodeDecodeError, JSONDecodeError) as e:
        logger.error(f"Error reading data.json: {e}")
        return {}

class StormContext(BaseModel):
    video_url: str = ""
    chat_url: str = ""
    messages: list[str] = []
    subscribe: tuple[bool, bool] = (False, False)
    subscribe_and_wait_time: int = 0
    slow_mode: int = 5
    channels: list[int] = []
    background: bool = False 

    target_channel: tuple[str, bool] = ("", False) # (channel_url, channel_url_fetched)
    total_instances: int = 0
    ready_to_storm_instances: int = 0
    total_channels: int = 0
    all_channels: dict[str, dict[str, Any]] = {}
    assigned_profiles: dict[str, int | None] = {}
    message_count: int = 0
    message_rate: float = 0.0
    each_channel_instances: list[Any] = Field(default=[], exclude=True)
    channels_status: dict[str, dict[str, Any]] = {}
    storm_status: Literal["Running", "Paused", "Stopped"] = "Running"
    start_time: str = datetime.now().isoformat()

    @model_validator(mode="before")
    @classmethod
    def check_channels(cls, values: dict) -> dict:
        file_data: dict = read_data_json()

        values["total_channels"] = file_data.get("no_of_channels", 0)

        channels: dict = file_data.get("channels", {})
        
        for channel in channels.values():
            channel["status"] = -1
        
        values["all_channels"] = channels

        return values


__all__: list[str] = ["StormContext"]

if __name__ == "__main__":
    context: StormContext = StormContext()
    print(context.model_dump_json(indent=4))