from json import load, JSONDecodeError 
from typing import Any, Literal
from logging import getLogger, Logger
from datetime import datetime 
from asyncio import Event, Lock 

from ..settings import settings

logger: Logger = getLogger(f"streamstorm.{__name__}")

class StormContext:
    def __init__(self):
        self.video_url: str = ""
        self.chat_url: str = ""
        self.messages: list[str] = []
        self.subscribe: tuple[bool, bool] = (False, False)
        self.subscribe_and_wait_time: int = 0
        self.slow_mode: int = 5
        self.channels: list[int] = []
        self.background: bool = False 

        self.target_channel: tuple[str, bool] = ("", False) # (channel_url, channel_url_fetched)
        self.total_instances: int = 0
        self.ready_to_storm_instances: int = 0
        self.total_channels: int = 0
        self.all_channels: dict[str, dict[str, Any]] = {}
        self.assigned_profiles: dict[str, int | None] = {}
        self.message_count: int = 0
        self.message_rate: float = 0.0
        self.each_channel_instances: list[Any] = []
        self.storm_status: Literal["Running", "Paused", "Stopped"] = "Running"
        self.start_time: str = datetime.now().isoformat()

        self.run_stopper_event: Event = Event()
        self.ready_event: Event = Event()
        self.pause_event: Event = Event()
        self.message_counter_lock: Lock = Lock()        

        self.initiate_channels()

    def read_data_json(self) -> dict:
        try:
            with open(settings.data_json_path, "r", encoding="utf-8") as file:
                return load(file)

        except (FileNotFoundError, PermissionError, UnicodeDecodeError, JSONDecodeError) as e:
            logger.error(f"Error reading data.json: {e}")
            return {}

    def initiate_channels(self) -> None:
        file_data: dict = self.read_data_json()

        self.total_channels = file_data.get("no_of_channels", 0)

        channels: dict = file_data.get("channels", {})
        
        for channel in channels.values():
            channel["status"] = -1
        
        self.all_channels = channels

    async def get(self) -> dict:
        context: dict = {}

        context["video_url"] = self.video_url
        context["chat_url"] = self.chat_url
        context["messages"] = self.messages
        context["subscribe"] = self.subscribe
        context["subscribe_and_wait_time"] = self.subscribe_and_wait_time
        context["slow_mode"] = self.slow_mode
        context["channels"] = self.channels
        context["background"] = self.background

        context["target_channel"] = self.target_channel
        context["total_instances"] = self.total_instances
        context["ready_to_storm_instances"] = self.ready_to_storm_instances
        context["total_channels"] = self.total_channels
        context["all_channels"] = self.all_channels
        context["assigned_profiles"] = self.assigned_profiles
        context["message_count"] = self.message_count
        context["message_rate"] = self.message_rate
        context["storm_status"] = self.storm_status
        context["start_time"] = self.start_time

        return context


__all__: list[str] = ["StormContext"]

if __name__ == "__main__":
    context: StormContext = StormContext()
    from json import dumps
    from asyncio import run
    print(dumps(run(context.get()), indent=4))