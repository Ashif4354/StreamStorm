from asyncio import Task, sleep, Event, create_task, gather, TimeoutError as AsyncTimeoutError, Lock
from random import choice
from os import environ
from os.path import join
from typing import Optional
from json import loads, JSONDecodeError
from http.client import RemoteDisconnected
from urllib3.exceptions import ProtocolError, ReadTimeoutError
from aiofiles import open as aio_open
from logging import getLogger, Logger
from contextlib import suppress
from datetime import datetime


from playwright.async_api import (
    Error as PlaywrightError, 
    TimeoutError as PlaywrightTimeoutError,
)
from playwright._impl._errors import TargetClosedError

from ..utils.exceptions import BrowserClosedError, ElementNotFound
from .SeparateInstance import SeparateInstance
from .Profiles import Profiles
from ..utils.clear_ram import clear_ram
from ..socketio.sio import sio
from ..api.validation import StormData

logger: Logger = getLogger(f"streamstorm.{__name__}")

class StreamStorm(Profiles):
    __slots__: tuple[str, ...] = (
        'url', 'chat_url', 'messages', 'subscribe', 'subscribe_and_wait_time', 
        'slow_mode', 'channels', 'background', 'ready_event', 'pause_event',
        'total_instances', 'ready_to_storm_instances', 'total_channels', 
        'all_channels', 'assigned_profiles', 'run_stopper_event', 'previous_count',
        'time_elapsed_since_last_minute', 'message_counter_lock', 'message_count',
        'storm_context', 'storm_data'
    )
    
    each_channel_instances: list[SeparateInstance] = []
    ss_instance: Optional["StreamStorm"] = None
    log_file_path: str = "" # Will be set by CustomLogger during logging setup

    def __init__(self, data: StormData) -> None:
        
        super().__init__()
        
        self.storm_data: dict = data.model_dump()
        self.url: str = f"{data.video_url}&hl=en-US&persist_hl=1"
        self.chat_url: str = f"{data.chat_url}&hl=en-US&persist_hl=1"
        self.messages: list[str] = data.messages
        self.subscribe: tuple[bool, bool] = (data.subscribe, data.subscribe_and_wait)
        self.subscribe_and_wait_time: int = data.subscribe_and_wait_time
        self.slow_mode: int = data.slow_mode
        self.channels: list[int] = sorted(data.channels)
        self.background: bool = data.background

        self.ready_event: Event = Event()
        self.pause_event: Event = Event()
        self.run_stopper_event: Event = Event()

        self.total_instances: int = len(data.channels)
        self.ready_to_storm_instances: int = 0
        self.total_channels: int = 0
        self.all_channels: dict[str, dict[str, str]] = {}

        self.assigned_profiles: dict[str, int] = {}
        self.message_counter_lock: Lock = Lock()
        self.message_count: int = 0
        self.storm_context: dict = {}

        StreamStorm.ss_instance = self

        logger.debug(f"StreamStorm initialized with url: {self.url}, channels: {self.channels}, "
                    f"messages count: {len(self.messages)}, slow_mode: {self.slow_mode}s, "
                    f"background: {self.background}")        
        
    async def emit_instance_status(self, index: int, status: int) -> None:
        str_index: str = str(index)
        self.storm_context["channels_status"][str_index]["status"] = status
        await sio.emit("instance_status", {"instance": str_index, "status": str(status)}, room="streamstorm")
        
    async def init_context(self) -> None:
        self.storm_context["storm_data"] = self.storm_data
        self.storm_context["channels_status"] = self.all_channels
        self.storm_context["storm_status"] = "Running"
        self.storm_context["start_time"] = datetime.now().isoformat()
        
    async def set_slow_mode(self, slow_mode: int) -> None:
        self.slow_mode = slow_mode
        logger.info(f"Slow mode set to {self.slow_mode} seconds")

    async def set_messages(self, messages: list[str]) -> None:
        self.messages = messages
        logger.info(f"Messages set to: {self.messages}")


    async def check_channels_available(self) -> None:
        logger.debug(f"Checking channel availability for profiles in: {self.profiles_dir}")
        
        try:
            async with aio_open(join(self.profiles_dir, "data.json"), "r", encoding="utf-8") as file:
                data: dict = loads(await file.read()) # We are using loads instead of load to avoid blocking the event loop
                
        except (FileNotFoundError, PermissionError, UnicodeDecodeError, JSONDecodeError) as e:
            logger.error("Failed to read data.json - profiles not created yet")
            raise SystemError("Create profiles first.") from e
            
        no_of_channels: int = data.get("no_of_channels", 0)

        self.total_channels = no_of_channels
        channels: dict = data.get("channels", {})
        
        for channel in channels.values():
            channel["status"] = -1
        
        self.all_channels = channels
        
        logger.info(f"Found {no_of_channels} channels in config, required: {len(self.channels)}")

        if no_of_channels < len(self.channels):
            logger.error(f"Insufficient channels: available={no_of_channels}, required={len(self.channels)}")
            raise SystemError("Not enough channels available in your YouTube Account. Create enough channels first. Then create Profiles again in the app.")
    
    async def get_active_channels(self) -> list[int]:
        active_channels: list[int] = []

        active_channels.extend(
            channel_index
            for channel_index in self.assigned_profiles.values()
            if channel_index is not None
        )
        return active_channels
        
    async def EachChannel(self, index: int, profile_dir: str, wait_time: float = 0) -> None:
        
        channel_name: str = self.all_channels[str(index)]['name']

        logger.info(f"[{index}] [{channel_name}] Using profile: {profile_dir}, Wait time: {wait_time}s")
        profile_dir_name: str=  profile_dir.split("\\")[-1]
        
        try:

            SI = SeparateInstance(
                index,
                profile_dir,
                self.background,
                profile_dir_name
            )
            
            await self.emit_instance_status(index, 1)  # 1 = Getting Ready

            SI.channel_name = channel_name

            self.assigned_profiles[profile_dir_name] = index

            logger.info(f"[{index}] [{channel_name}] Assigned profile {profile_dir_name}")

            StreamStorm.each_channel_instances.append(SI)
            
            logger.info(f"[{index}] [{channel_name}] Attempting login...")
            logged_in: bool = await SI.login()
            
            self.run_stopper_event.set()  # Set the event to signal that stopper can check for instance errors
            logger.debug(f"[{index}] [{channel_name}] Run stopper event set")
            
            if not logged_in:
                logger.debug(f"[{index}] [{channel_name}] Login failed - removing from instances")
                
                self.total_instances -= 1
                self.assigned_profiles[profile_dir_name] = None
                
                StreamStorm.each_channel_instances.remove(SI)
                
                logger.error(f"[{index}] [{channel_name}] : Login failed")
                await self.emit_instance_status(index, 0)  # 0 = Dead
                
                return

            logger.info(f"[{index}] [{channel_name}] Login successful")

            if self.subscribe[0]:
                logger.debug(f"[{index}] [{channel_name}] Navigating to subscribe URL: {self.url}")
                
                await SI.go_to_page(self.url)
                await SI.subscribe_to_channel()
                
                logger.info(f"[{index}] [{channel_name}] Subscription attempt completed")

            await SI.page.set_viewport_size({"width": 500, "height": 900})
            logger.info(f"[{index}] [{channel_name}] Navigating to chat URL: {self.chat_url}")
            await SI.go_to_page(self.chat_url)
            
            self.ready_to_storm_instances += 1
            logger.info(f"[{index}] [{channel_name}] : Ready To Storm")
            await self.emit_instance_status(index, 2)  # 2 = Ready

            if self.subscribe[1]:
                logger.info(f"[{index}] [{channel_name}] Waiting {self.subscribe_and_wait_time}s after subscription")
                await sleep(self.subscribe_and_wait_time)
                 
                
            logger.debug(f"[{index}] [{channel_name}] Waiting for ready event...")
            await self.ready_event.wait() # Wait for the ready event to be set before starting the storming
            
            logger.debug(f"[{index}] [{channel_name}] Starting storm loop with {wait_time}s initial delay")
            await self.emit_instance_status(index, 3)  # 3 = Storming
            
            await sleep(wait_time)  # Wait for the initial delay before starting to storm

            while True:
                await self.pause_event.wait()
        
                # input()
                selected_message = choice(self.messages)
                logger.debug(f"[{index}] [{channel_name}] Sending message: '{selected_message}'")
                
                try:
                    await SI.send_message(selected_message)
                    
                    async with self.message_counter_lock:
                        self.message_count += 1
                        
                    logger.debug(f"[{index}] [{channel_name}] Message sent successfully")
                    
                except (BrowserClosedError, ElementNotFound, TargetClosedError):
                    logger.debug(f"[{index}] [{channel_name}] : ##### Browser/element error - cleaning up instance")
                    logger.error(f"[{index}] [{channel_name}] : Error in finding chat field")
                    await self.emit_instance_status(index, 0)  # 0 = Dead

                    self.assigned_profiles[profile_dir_name] = None
                    
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
                    break
                
                logger.debug(f"[{index}] [{channel_name}] Sleeping for {self.slow_mode}s before next message")
                await sleep(self.slow_mode)

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
        
    def get_start_storm_wait_time(self, index, no_of_profiles, slow_mode) -> float:
        return index * (slow_mode / no_of_profiles)
    
    async def messages_handler(self) -> None:
        time_frame: int = 2 # time frame in seconds to send message count updates
        self.previous_count: int = 0
        self.time_elapsed_since_last_minute: int = 0 # in seconds
        message_rate: float = 0.0
        
        logger.debug("#### Starting message handler...")
        await self.ready_event.wait()  # Wait for the ready event to be set before starting the storming    
        
        async def reset_message_count() -> None:
            while StreamStorm.ss_instance is not None:
                await sleep(60) # asyncio.sleep
                
                async with self.message_counter_lock:
                    self.previous_count = self.message_count
                    
                self.time_elapsed_since_last_minute = 0  # Reset time elapsed every minute
                
                logger.debug(f"Message count for the last minute reset to {self.previous_count}")
                
                
        create_task(reset_message_count())
        
        while StreamStorm.ss_instance is not None:
            
            async with self.message_counter_lock:
                current_count: int = self.message_count - self.previous_count            
            
            await sio.emit('total_messages', {'total_messages': self.message_count}, room="streamstorm")
            
            self.time_elapsed_since_last_minute += time_frame
            
            message_rate = ((current_count / self.time_elapsed_since_last_minute) * 60) if self.time_elapsed_since_last_minute > 0 else message_rate
            
            await sio.emit('messages_rate', {'message_rate': message_rate}, room="streamstorm")
            await sleep(time_frame) # asyncio.sleep
            
        # I know the time may have a difference of 1-3 seconds but it's not a big deal.
        # This is just an average value for UI display purpose only, not an accurate value.
        

    async def start(self) -> None:  
        
        clear_ram()       

        self.ready_event.clear()  # Wait for the ready event to be set before starting the storming
        self.ready_to_storm_instances = 0
        
        await self.check_channels_available()
        
        await self.init_context()
        
        if self.channels[-1] > self.total_channels:
            raise SystemError("You have selected more channels than available channels in your YouTube channel. Create enough channels first.")
        
        
        temp_profiles: list[str] = self.get_available_temp_profiles()
        no_of_temp_profiles: int = len(temp_profiles)
        
        self.assigned_profiles = {profile: None for profile in temp_profiles}
        
        
        
        if no_of_temp_profiles < len(self.channels):
            raise SystemError("Not enough temp profiles available. Create Enough profiles first.")       
        

        async def start_each_worker() -> None:
            
            await sleep(3)  # Small delay to ensure everything is set up in UI before starting workers

            async def wait_for_all_worker_to_be_ready() -> None:
                while self.ready_to_storm_instances < self.total_instances:
                    await sleep(1)
                logger.info(f"All {self.total_instances} instances ready - starting storm")
                self.ready_event.set()  # Set the event to signal that all instances are ready

            create_task(wait_for_all_worker_to_be_ready())
            create_task(self.messages_handler())
            
            tasks: list[Task] = []
            for index in range(len(self.channels)):
                profile_dir: str = join(self.profiles_dir, temp_profiles[index])
                wait_time: float = self.get_start_storm_wait_time(index, no_of_temp_profiles, self.slow_mode)

                # executor.submit(self.EachChannel, self.channels[index], profile_dir, wait_time)
                task: Task = create_task(self.EachChannel(self.channels[index], profile_dir, wait_time))
                tasks.append(task)
                await sleep(0.2)  # Small delay to avoid instant spike of the cpu load

            await gather(*tasks)  # Wait for all tasks to complete
            environ.update({"BUSY": "0"})

            self.run_stopper_event.clear()
            StreamStorm.ss_instance = None
            StreamStorm.each_channel_instances.clear()
            logger.debug("All Coroutines completed")

        create_task(start_each_worker())
    
    async def start_more_channels(self, channels: list[int]) -> None:
        
        async def get_profiles() -> tuple[bool, list[str]]:
            count: int = 0
            available_profiles: list[str] = []
            for key, value in self.assigned_profiles.items():
                if value is None:
                    count += 1
                    available_profiles.append(key)

            return count >= len(channels), available_profiles[:len(channels)]

        enough_profiles, available_profiles = await get_profiles()

        already_running_channels: list[int] = self.assigned_profiles.values()

        for channel in channels:
            if channel in already_running_channels:
                raise SystemError(f"Channel {channel} : {self.all_channels[str(channel)]['name']} is already running.")
        if not enough_profiles:
            raise SystemError("Not enough available profiles to start more channels.")
        
        async def start_each_worker() -> None:  
            
            tasks: list[Task] = []   
            for index in range(len(channels)):
                profile_dir: str = join(self.profiles_dir, available_profiles[index])
                wait_time: float = self.get_start_storm_wait_time(index, len(available_profiles), self.slow_mode)

                task: Task = create_task(self.EachChannel(channels[index], profile_dir, wait_time))
                tasks.append(task)
                await sleep(0.2)

            await gather(*tasks)
            logger.debug("All Coroutines completed")

        create_task(start_each_worker())       


__all__: list[str] = ["StreamStorm"]
