from asyncio import Task, sleep, Event, create_task, gather, TimeoutError as AsyncTimeoutError, Lock
from random import choice
from os.path import join
from typing import Optional, Literal
from http.client import RemoteDisconnected
from urllib3.exceptions import ProtocolError, ReadTimeoutError
from logging import getLogger, Logger
from contextlib import suppress
from urllib.parse import urlparse, parse_qs, ParseResult
from json import load, JSONDecodeError

from playwright.async_api import (
    Error as PlaywrightError, 
    TimeoutError as PlaywrightTimeoutError,
)
from playwright._impl._errors import TargetClosedError
from yt_dlp import YoutubeDL

from ..utils.exceptions import BrowserClosedError, ElementNotFound
from ..utils.cookies import get_cookies
from .SeparateInstance import SeparateInstance
from .Profiles import Profiles
from .StormContext import StormContext
from ..socketio.sio import sio
from ..api.validation import StormData
from ..settings import settings

logger: Logger = getLogger(f"streamstorm.{__name__}")

class StreamStorm(Profiles):
    __slots__: tuple[str, ...] = (
        'ready_event', 'pause_event', 'run_stopper_event', 
        'message_counter_lock', 'context', 'cookies'
    )
    
    ss_instance: Optional["StreamStorm"] = None

    def __init__(self, data: StormData) -> None:
        
        super().__init__()
        
        self.context: StormContext = StormContext()
        self.ready_event: Event = Event()
        self.pause_event: Event = Event()
        self.run_stopper_event: Event = Event()
        self.message_counter_lock: Lock = Lock()

        self.init_context(data)
        self.load_cookies()

        StreamStorm.ss_instance = self

        logger.debug(f"Storm initialized with url: {self.context.video_url}, channels: {self.context.channels}, "
                    f"messages count: {len(self.context.messages)}, slow_mode: {self.context.slow_mode}s, "
                    f"background: {self.context.background}")        
        
    async def emit_instance_status(self, index: int, status: int) -> None:
        str_index: str = str(index)
        self.context.all_channels[str_index]["status"] = status
        await sio.emit("instance_status", {"instance": str_index, "status": str(status)}, room="streamstorm")
        
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
            raise SystemError("Cookies not found: Login First")
        
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
        
    async def EachChannel(self, index: int, channel_name: str, profile_dir: str, wait_time: float = 0) -> None:

        logger.info(f"[{index}] [{channel_name}] Using profile: {profile_dir}, Wait time: {wait_time}s")
        profile_dir_name: str=  profile_dir.split("\\")[-1]
        
        try:

            SI = SeparateInstance(
                index,
                profile_dir,
                self.context.background,
                profile_dir_name,
                wait_time,
                self.cookies
            )
            
            await self.emit_instance_status(index, 1)  # 1 = Getting Ready

            SI.channel_name = channel_name

            self.context.assigned_profiles[profile_dir_name] = index

            logger.info(f"[{index}] [{channel_name}] Assigned profile {profile_dir_name}")

            StreamStorm.each_channel_instances.append(SI)
            
            logger.info(f"[{index}] [{channel_name}] Attempting login...")
            logged_in: bool = await SI.login()
            
            self.run_stopper_event.set()  # Set the event to signal that stopper can check for instance errors
            logger.debug(f"[{index}] [{channel_name}] Run stopper event set")
            
            if not logged_in:
                logger.debug(f"[{index}] [{channel_name}] Login failed - removing from instances")
                
                self.context.total_instances -= 1
                self.context.assigned_profiles[profile_dir_name] = None
                
                StreamStorm.each_channel_instances.remove(SI)
                
                logger.error(f"[{index}] [{channel_name}] : Login failed")
                await self.emit_instance_status(index, 0)  # 0 = Dead
                
                return

            logger.info(f"[{index}] [{channel_name}] Login successful")

            if self.context.subscribe[0]:
                logger.debug(f"[{index}] [{channel_name}] Navigating to subscribe URL: {self.context.video_url}")
                
                await SI.go_to_page(self.context.target_channel[0])
                await SI.subscribe_to_channel(self.context.target_channel[1])
                
                logger.info(f"[{index}] [{channel_name}] Subscription attempt completed")

            await SI.page.set_viewport_size({"width": 500, "height": 900})
            logger.info(f"[{index}] [{channel_name}] Navigating to chat URL: {self.context.chat_url}")
            await SI.go_to_page(self.context.chat_url)
            
            self.context.ready_to_storm_instances += 1
            logger.info(f"[{index}] [{channel_name}] : Ready To Storm")
            await self.emit_instance_status(index, 2)  # 2 = Ready

            if self.context.subscribe[1]:
                logger.info(f"[{index}] [{channel_name}] Waiting {self.context.subscribe_and_wait_time}s after subscription")
                await sleep(self.context.subscribe_and_wait_time)
                 
                
            logger.debug(f"[{index}] [{channel_name}] Waiting for ready event...")
            await self.ready_event.wait() # Wait for the ready event to be set before starting the storming
            
            logger.debug(f"[{index}] [{channel_name}] Starting storm loop with {wait_time}s initial delay")
            await self.emit_instance_status(index, 3)  # 3 = Storming

            while True:
                await self.pause_event.wait()
                if SI.should_wait:
                    await sleep(SI.wait_time)
                    SI.should_wait = False
        
                # input()
                selected_message = choice(self.context.messages)
                logger.debug(f"[{index}] [{channel_name}] Sending message: '{selected_message}'")
                
                try:
                    await SI.send_message(selected_message)
                    
                    async with self.message_counter_lock:
                        self.context.message_count += 1
                        
                    logger.debug(f"[{index}] [{channel_name}] Message sent successfully")
                    
                except (BrowserClosedError, ElementNotFound, TargetClosedError):
                    logger.debug(f"[{index}] [{channel_name}] : ##### Browser/element error - cleaning up instance")
                    logger.error(f"[{index}] [{channel_name}] : Error in finding chat field")
                    await self.emit_instance_status(index, 0)  # 0 = Dead

                    self.context.assigned_profiles[profile_dir_name] = None
                    
                    try:
                        await SI.page.close()
                    except PlaywrightError as e:
                        logger.error(f"[{index}] [{channel_name}] : Error closing page: {e}")
                        
                    
                    with suppress(ValueError):
                        StreamStorm.each_channel_instances.remove(SI)
                        logger.debug(f"[{index}] [{channel_name}] : Removed from instances")                        
                    
                    break
                    
                except Exception as e:
                    logger.error(f"[{index}] [{channel_name}] : New Error ({type(e).__name__}): {e}")
                    await self.emit_instance_status(index, 0)  # 0 = Dead
                    self.context.assigned_profiles[profile_dir_name] = None

                    try:
                        await SI.page.close()
                    except PlaywrightError as e:
                        logger.error(f"[{index}] [{channel_name}] : Error closing page: {e}")
                    finally:
                        break
                
                logger.debug(f"[{index}] [{channel_name}] Sleeping for {self.context.slow_mode}s before next message")
                await sleep(self.context.slow_mode)

        except (
            RemoteDisconnected,
            ProtocolError,
            ReadTimeoutError,
            ConnectionResetError,
            TimeoutError,
            AsyncTimeoutError,
            PlaywrightError,
            PlaywrightTimeoutError,
            BrowserClosedError
        ) as e:
            logger.error(f"[{index}] [{channel_name}] : Error: {e}")
            await self.emit_instance_status(index, 0)  # 0 = Dead
            self.context.assigned_profiles[profile_dir_name] = None

            try:
                await SI.page.close()
            except PlaywrightError as e:
                logger.error(f"[{index}] [{channel_name}] : Error closing page: {e}")
        
    def get_start_storm_wait_time(self, index) -> float:
        return index * (self.context.slow_mode / self.context.total_instances)
    
    async def messages_handler(self) -> None:
        time_frame: int = 2 # time frame in seconds to send message count updates
        previous_count: int = 0
        time_elapsed_since_last_minute: int = 0 # in seconds
        
        logger.debug("#### Starting message handler...")
        await self.ready_event.wait()  # Wait for the ready event to be set before starting the storming    
        
        async def reset_message_count() -> None:
            nonlocal previous_count, time_elapsed_since_last_minute
            
            while StreamStorm.ss_instance is not None:
                await sleep(60) # asyncio.sleep
                
                async with self.message_counter_lock:
                    previous_count = self.context.message_count
                    
                time_elapsed_since_last_minute = 0  # Reset time elapsed every minute
                
                logger.debug(f"Message count for the last minute reset to {previous_count}")
                
                
        create_task(reset_message_count())
        
        while StreamStorm.ss_instance is not None:
            
            async with self.message_counter_lock:
                current_count: int = self.context.message_count - previous_count            
            
            await sio.emit('total_messages', {'total_messages': self.context.message_count}, room="streamstorm")
            
            time_elapsed_since_last_minute += time_frame
            
            self.context.message_rate = ((current_count / time_elapsed_since_last_minute) * 60) if time_elapsed_since_last_minute > 0 else 0.0
            
            await sio.emit('messages_rate', {'message_rate': self.context.message_rate}, room="streamstorm")
            await sleep(time_frame) # asyncio.sleep
            
        # I know the time may have a difference of 1-3 seconds but it's not a big deal.
        # This is just an average value for UI display purpose only, not an accurate value.
        

    async def start(self) -> None:       

        self.ready_event.clear()  # Wait for the ready event to be set before starting the storming
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
                self.ready_event.set()  # Set the event to signal that all instances are ready

            create_task(wait_for_all_worker_to_be_ready())
            create_task(self.messages_handler())
            
            tasks: list[Task] = []
            for index in range(len(self.context.channels)):
                profile_dir: str = join(self.environment_dir, temp_profiles[index])
                channel_name: str = self.context.all_channels[str(self.context.channels[index])]['name']
                wait_time: float = self.get_start_storm_wait_time(index)
   
                logger.debug(f"[{index}] [{channel_name}] Wait time: {wait_time}")

                task: Task = create_task(self.EachChannel(self.context.channels[index], channel_name, profile_dir, wait_time))
                tasks.append(task)
                await sleep(0.2)  # Small delay to avoid instant spike of the cpu load

            await gather(*tasks)  # Wait for all tasks to complete

            logger.debug("Initial storm instances completed")

        create_task(start_each_worker())
    
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

        already_running_channels: list[int] = self.context.assigned_profiles.values()

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

                task: Task = create_task(self.EachChannel(channels[index], channel_name, profile_dir, wait_time))
                tasks.append(task)
                await sleep(0.2)

            await gather(*tasks)
            logger.debug("All added instances completed")

        create_task(start_each_worker())       


__all__: list[str] = ["StreamStorm"]
