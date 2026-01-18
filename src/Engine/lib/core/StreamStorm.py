from asyncio import Task, sleep, Event, create_task, gather, Lock
from os.path import join
from typing import Optional, Literal
from logging import getLogger, Logger
from urllib.parse import urlparse, parse_qs, ParseResult

from yt_dlp import YoutubeDL

from ..utils.cookies import get_cookies
from .SeparateInstance import SeparateInstance
from .Profiles import Profiles
from .StormContext import StormContext
from ..socketio.sio import sio
from ..api.validation import StormData
from ..settings import settings

logger: Logger = getLogger(f"streamstorm.{__name__}")

class StreamStorm(Profiles):
    __slots__: tuple[str, ...] = ('context', 'cookies', '_background_tasks')
    
    ss_instance: Optional["StreamStorm"] = None

    def __init__(self, data: StormData) -> None:
        
        super().__init__()
        
        self.context: StormContext = StormContext()                
        self._background_tasks: list[Task] = []

        self.init_context(data)
        self.load_cookies()

        StreamStorm.ss_instance = self

        logger.debug(f"Storm initialized with url: {self.context.video_url}, channels: {self.context.channels}, "
                    f"messages count: {len(self.context.messages)}, slow_mode: {self.context.slow_mode}s, "
                    f"background: {self.context.background}")        
        
    
        
    def init_context(self, storm_data: StormData) -> None:

        self.context.video_url = storm_data.video_url
        self.context.chat_url = storm_data.chat_url
        self.context.messages = storm_data.messages
        self.context.subscribe = (storm_data.subscribe, storm_data.subscribe_and_wait)
        self.context.subscribe_and_wait_time = storm_data.subscribe_and_wait_time
        self.context.slow_mode = storm_data.slow_mode
        self.context.channels = sorted(storm_data.channels)
        self.context.background = storm_data.background
        self.context.target_channel = self.get_channel_url()
        self.context.total_instances = len(storm_data.channels)
        self.context.ready_to_storm_instances = 0
        self.context.assigned_profiles = {}
        self.context.message_count = 0
        self.context.message_rate = 0.0
        

    def load_cookies(self) -> None:

        cookies: list = get_cookies()
        
        if not cookies and settings.login_method == "cookies":
            raise SystemError("Cookies not found or invalid: Try logging in again")
        
        self.cookies = cookies
            
        # try:
        #     with open(settings.cookies_path, "r") as f:
        #         self.cookies = load(f)
                
        # except (FileNotFoundError, JSONDecodeError):
        #     if settings.login_method == "cookies":
        #         raise SystemError("Cookies not found: Login again")
        #     else:
        #         self.cookies = []
        

    def get_redirect_url(self, url: str, type: Literal["video", "channel", "uploader", "chat"]) -> str:
        """
        Redirects to the given url with the given type

        We are redirecting from "https://streamstorm.darkglance.in" because The developer(me) wants to show
        the traffic came from StreamStorm application in youtube analytics. (Just for fun)
        """

        parsed_url: ParseResult = urlparse(url)
        final_url: ParseResult = urlparse("https://streamstorm.darkglance.in")

        if type == "video":
            video_id: str = parse_qs(parsed_url.query).get("v")[0]

            # url = f"https://streamstorm.darkglance.in/v/{video_id}?hl=en-US&persist_hl=1" 
            final_url = final_url._replace(path=f"/v/{video_id}")

        elif type == "channel":
            channel_id: str = parsed_url.path.split("/")[-1]

            # url = f"https://streamstorm.darkglance.in/c/{channel_id}?hl=en-US&persist_hl=1"
            final_url = final_url._replace(path=f"/c/{channel_id}")

        elif type == "uploader":
            uploader_id: str = parsed_url.path

            # url = f"https://streamstorm.darkglance.in/u/{uploader_id}?hl=en-US&persist_hl=1"
            final_url = final_url._replace(path=f"/u/{uploader_id}")

        elif type == "chat":
            chat_id: str = parse_qs(parsed_url.query).get("v")[0]

            # url = f"https://streamstorm.darkglance.in/ch/{chat_id}?hl=en-US&persist_hl=1"
            final_url = final_url._replace(path=f"/ch/{chat_id}")
        
        final_url = final_url._replace(query="hl=en-US&persist_hl=1")
        
        # When redirecting to channel or uploader url it redirect to "/search" page of the channel or uploader url
        # This is done to load the page faster
        # This is handled in vercel.json in src/Site
        return final_url.geturl()
        
    def get_channel_url(self) -> tuple[str, bool]:
        ytdlp_options: dict = {
            "quiet": True,
            # "dump_single_json": True,
            "extract_flat": True
        }
        
        try:
            with YoutubeDL(ytdlp_options) as ytdlp:
                info_dict: dict = ytdlp.extract_info(self.context.video_url, download=False)
                
                channel_url: str = info_dict.get("channel_url")
                if channel_url:
                    final_url: str = self.get_redirect_url(channel_url, "channel")
                    return final_url, True
                
                uploader_url: str = info_dict.get("uploader_url")
                if uploader_url:
                    final_url: str = self.get_redirect_url(uploader_url, "uploader")
                    return final_url, True

                raise Exception("Channel or uploader url not found")
                
        except Exception as e:
            logger.error(f"Failed to fetch channel url: {e}")
            return self.get_redirect_url(self.context.video_url, "video"), False
        
        
        
    async def set_slow_mode(self, slow_mode: int) -> None:
        self.context.slow_mode = slow_mode
        logger.info(f"Slow mode set to {self.context.slow_mode} seconds")


    async def set_messages(self, messages: list[str]) -> None:
        self.context.messages = messages
        logger.info(f"Messages set to: {self.context.messages}")


    async def check_channels_available(self) -> None:
        logger.debug(f"Checking channel availability for profiles in: {self.environment_dir}")

        if self.context.all_channels == {}:
            logger.error("Failed to read data.json - Not logged in")
            raise SystemError("Login first.")

        logger.info(f"Found {self.context.total_channels} channels in config, required: {len(self.context.channels)}")

        if self.context.total_channels < len(self.context.channels):
            logger.error(f"Insufficient channels: available={self.context.total_channels}, required={len(self.context.channels)}")
            raise SystemError("Not enough channels available in your YouTube Account. Create enough channels first. Then create Profiles again in the app.")
    

    async def get_active_channels(self) -> list[int]:
        active_channels: list[int] = []

        active_channels.extend(
            channel_index
            for channel_index in self.context.assigned_profiles.values()
            if channel_index is not None
        )

        return active_channels  
               
        
    def get_start_storm_wait_time(self, index) -> float:
        if self.context.total_instances == 0:
            return 0.0
        return index * (self.context.slow_mode / self.context.total_instances)
    
    def _track_task(self, task: Task) -> Task:
        """Track a background task for later cleanup."""
        self._background_tasks.append(task)
        return task

    
    async def cleanup(self) -> None:
        """Cancel all background tasks and clean up resources."""
        logger.info("Starting StreamStorm cleanup...")
        
        for task in self._background_tasks:
            if not task.done():
                task.cancel()
                logger.debug(f"Cancelled task: {task.get_name()}")
        
        # Wait for all tasks to complete cancellation
        if self._background_tasks:
            await gather(*self._background_tasks, return_exceptions=True)
        
        self._background_tasks.clear()
        self.context.each_channel_instances.clear()
        
        logger.info("StreamStorm cleanup completed")

    
    async def messages_handler(self) -> None:
        time_frame: int = 2 # time frame in seconds to send message count updates
        previous_count: int = 0
        time_elapsed_since_last_minute: int = 0 # in seconds
        
        logger.debug("#### Starting message handler...")
        await self.context.ready_event.wait()  # Wait for the ready event to be set before starting the storming    
        
        async def reset_message_count() -> None:
            nonlocal previous_count, time_elapsed_since_last_minute
            
            while StreamStorm.ss_instance is not None:
                await sleep(60) # asyncio.sleep
                
                async with self.context.message_counter_lock:
                    previous_count = self.context.message_count
                    
                time_elapsed_since_last_minute = 0  # Reset time elapsed every minute
                
                logger.debug(f"Message count for the last minute reset to {previous_count}")                
                
        self._track_task(create_task(reset_message_count()))
        
        while StreamStorm.ss_instance is not None:
            
            async with self.context.message_counter_lock:
                current_count: int = self.context.message_count - previous_count            
            
            await sio.emit('total_messages', {'total_messages': self.context.message_count}, room="streamstorm")
            
            time_elapsed_since_last_minute += time_frame
            
            self.context.message_rate = ((current_count / time_elapsed_since_last_minute) * 60) if time_elapsed_since_last_minute > 0 else 0.0
            
            await sio.emit('messages_rate', {'message_rate': self.context.message_rate}, room="streamstorm")
            await sleep(time_frame) # asyncio.sleep
            
        # I know the time may have a difference of 1-3 seconds but it's not a big deal.
        # This is just an average value for UI display purpose only, not an accurate value.
        

    async def start(self) -> None:       

        self.context.ready_event.clear()  # Wait for the ready event to be set before starting the storming
        # self.context.ready_to_storm_instances = 0
        
        await self.check_channels_available()
        
        if self.context.channels[-1] > self.context.total_channels:
            raise SystemError("You have selected more channels than available channels in your YouTube channel. Create enough channels first.")
        
        
        temp_profiles: list[str] = self.get_available_temp_profiles(total_channels=self.context.total_channels)
        no_of_temp_profiles: int = len(temp_profiles)
        
        self.context.assigned_profiles = {profile: None for profile in temp_profiles}      
        
        if no_of_temp_profiles < len(self.context.channels):
            raise SystemError("Not enough temp profiles available. Create Enough profiles first.")     

        async def start_each_worker() -> None:
            
            await sleep(3)  # Small delay to ensure everything is set up in UI before starting workers

            await sio.emit("storm_started", room="streamstorm") # Emit storm started event to UI so that any extra connected clients know that the storm has started and will be able to hop in.

            async def wait_for_all_worker_to_be_ready() -> None:
                while self.context.ready_to_storm_instances < self.context.total_instances:
                    await sleep(1)
                logger.info(f"All {self.context.total_instances} instances ready - starting storm")
                self.context.ready_event.set()  # Set the event to signal that all instances are ready

            self._track_task(create_task(wait_for_all_worker_to_be_ready()))
            self._track_task(create_task(self.messages_handler()))
            
            tasks: list[Task] = []

            for index in range(len(self.context.channels)):
                profile_dir: str = join(self.environment_dir, temp_profiles[index])
                channel_name: str = self.context.all_channels[str(self.context.channels[index])]['name']
                wait_time: float = self.get_start_storm_wait_time(index)
   
                logger.info(f"[{index}] [{channel_name}] Using profile: {profile_dir}, Wait time: {wait_time}s")

                si: SeparateInstance = SeparateInstance(self.context.channels[index], profile_dir, wait_time, channel_name, self.cookies, self.context)

                task: Task = create_task(si.start())
                tasks.append(task)
                await sleep(0.2)  # Small delay to avoid instant spike of the cpu load

            await gather(*tasks)  # Wait for all tasks to complete

            logger.debug("Initial storm instances completed")

        self._track_task(create_task(start_each_worker()))
    
    async def start_more_channels(self, channels: list[int]) -> None:
        
        async def get_profiles() -> tuple[bool, list[str]]:
            count: int = 0
            available_profiles: list[str] = []

            for key, value in self.context.assigned_profiles.items():
                if value is None:
                    count += 1
                    available_profiles.append(key)

            return count >= len(channels), available_profiles[:len(channels)]

        enough_profiles, available_profiles = await get_profiles()

        already_running_channels = self.context.assigned_profiles.values()

        for channel in channels:
            if channel in already_running_channels:
                raise SystemError(f"Channel {channel} : {self.context.all_channels[str(channel)]['name']} is already running.")
                
        if not enough_profiles:
            raise SystemError("Not enough available profiles to start more channels.")

        self.context.total_instances += len(channels)
        
        async def start_each_worker() -> None:  
            
            tasks: list[Task] = [] 
              
            for index in range(len(channels)):
                profile_dir: str = join(self.environment_dir, available_profiles[index])
                channel_name: str = self.context.all_channels[str(channels[index])]['name']
                wait_time: float = self.get_start_storm_wait_time(index)

                logger.debug(f"[{index}] [{channel_name}] Wait time: {wait_time}")

                si: SeparateInstance = SeparateInstance(channels[index], profile_dir, wait_time, channel_name, self.cookies, self.context)

                task: Task = create_task(si.start())
                tasks.append(task)
                await sleep(0.2)

            await gather(*tasks)
            logger.debug("All added instances completed")

        self._track_task(create_task(start_each_worker()))       


__all__: list[str] = ["StreamStorm"]
