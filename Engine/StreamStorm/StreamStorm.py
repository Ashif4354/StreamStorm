from time import sleep
from threading import Thread
from random import choice
from os import environ
from typing import Self
from json import load
from http.client import RemoteDisconnected
from urllib3.exceptions import ProtocolError, ReadTimeoutError
from concurrent.futures import ThreadPoolExecutor
from threading import Event

from selenium.common.exceptions import InvalidSessionIdException

from .Selenium import Selenium
from .SeparateInstance import SeparateInstance
from .Profiles import Profiles
from .Lib import clear_ram


class StreamStorm(Selenium, Profiles):
    each_channel_instances: list[SeparateInstance] = []
    ss_instance: Self = None

    def __init__(
        self,
        url: str,
        chat_url: str,
        messages: list[str] = ["Hello", "Hi"],
        subscribe: tuple[bool, bool] = (False, False),
        subscribe_and_wait_time: int = 70,
        slow_mode: int = 0,
        # start_channel_index: int = 1,
        # end_channel_index: int = 10,
        channels: list[int] = None,
        browser: str = "edge",
        background: bool = True,
        shared_data: dict = None,
    ) -> None:
        
        Profiles.__init__(self, browser=browser)
        
        self.url: str = url
        self.chat_url: str = chat_url
        self.messages: list[str] = messages
        self.subscribe: tuple[bool, bool] = subscribe
        self.subscribe_and_wait_time: int = subscribe_and_wait_time
        self.slow_mode: int = slow_mode
        # self.start_channel_index: int = start_channel_index
        # self.end_channel_index: int = end_channel_index
        self.channels: list[int] = sorted(channels)
        self.browser: str = browser
        self.background: bool = background
        
        self.shared_data: dict = shared_data
        
        self.ready_event: Event = Event()
        self.pause_event: Event = Event()
        
        self.total_instances: int = len(channels)
        self.ready_to_storm_instances: int = 0
        self.total_channels: int = 0
        self.all_channels: dict[str, dict[str, str]] = {}
        
        self.assigned_profiles: dict[str, int] = {}
        
        StreamStorm.ss_instance = self
        
        clear_ram()
        
    def set_slow_mode(self, slow_mode: int) -> None:
        self.slow_mode = slow_mode
        print(f"Slow mode set to {self.slow_mode} seconds")
        
    def set_messages(self, messages: list[str]) -> None:
        self.messages = messages
        print(f"Messages set to: {self.messages}")
        
        
    def check_channels_available(self) -> None:
        try:
            with open(self.profiles_dir + r"\config.json", "r", encoding="utf-8") as file:
                data: dict = load(file)
        except FileNotFoundError:
            raise SystemError("Create profiles first.")
            
        no_of_channels: int = data.get("no_of_channels", 0)

        self.total_channels = no_of_channels
        self.all_channels = data.get("channels", {})

        if no_of_channels < len(self.channels):
            raise SystemError("Not enough channels available in your YouTube Account. Create enough channels first. Then create Profiles again in the app.")

    def get_active_channels(self) -> list[int]:
        active_channels: list[int] = []
        
        for channel_index in self.assigned_profiles.values():
            if channel_index is not None:
                active_channels.append(channel_index)
                
        return active_channels
        
    def EachChannel(self, index: int, profile_dir: str, wait_time: float = 0) -> None:
        
        print(f"Using profile: {profile_dir}")
        profile_dir_name: str=  profile_dir.split("\\")[-1]
        
        try:

            SI = SeparateInstance(
                index,
                profile_dir,
                self.browser,
                self.background,
            )

            self.assigned_profiles[profile_dir_name] = index

            print("Assigned profile to channel:", index)

            StreamStorm.each_channel_instances.append(SI)
            logged_in: bool = SI.login()
            
            if not logged_in:
                self.total_instances -= 1
                self.assigned_profiles[profile_dir_name] = None
                StreamStorm.each_channel_instances.remove(SI)
                print(f"========================= Login failed on channel {index} : {self.all_channels[str(index)]['name']}. =========================")
                return

            if self.subscribe[0]:
                SI.go_to_page(self.url)
                SI.subscribe_to_channel()

            SI.driver.set_window_size(500, 800)
            SI.go_to_page(self.chat_url)
            
            self.ready_to_storm_instances += 1
            print(f"@@@@@@@@@@@@@@@@@@@@@@@@@ Channel {index} : {self.all_channels[str(index)]['name']} is ready @@@@@@@@@@@@@@@@@@@@@@@@@")

            if self.subscribe[1]:
                sleep(self.subscribe_and_wait_time)
                 
                
            self.ready_event.wait() # Wait for the ready event to be set before starting the storming

            sleep(wait_time)  # Wait for the initial delay before starting to storm

            while True:
                self.pause_event.wait()
        
                # input()
                SI.send_message(choice(self.messages))
                sleep(self.slow_mode)

        except (
            InvalidSessionIdException,
            RemoteDisconnected,
            ProtocolError,
            ReadTimeoutError,
            ConnectionResetError,
            TimeoutError,
        ) as e:
            print(f"Error in channel {index}: {e}")
            pass
        
    def get_start_storm_wait_time(self, index, no_of_profiles, slow_mode) -> float:
        return index * (slow_mode / no_of_profiles)

    def start(self) -> None:       
        

        self.ready_event.clear()  # Wait for the ready event to be set before starting the storming
        self.ready_to_storm_instances = 0
        
        self.check_channels_available()
        
        if self.channels[-1] > self.total_channels:
            raise SystemError("You have selected more channels than available channels in your YouTube channel. Create enough channels first.")
        
        
        temp_profiles: list[str] = self.get_available_temp_profiles()
        no_of_temp_profiles: int = len(temp_profiles)
        
        self.assigned_profiles = {profile: None for profile in temp_profiles}
        
        
        
        if no_of_temp_profiles < len(self.channels):
            raise SystemError("Not enough temp profiles available. Create Enough profiles first.")       
        

        def start_each_worker() -> None:
            
            def wait_for_all_worker_to_be_ready() -> None:
                while self.ready_to_storm_instances < self.total_instances:
                    sleep(1)
                self.ready_event.set()  # Set the event to signal that all instances are ready

            Thread(target=wait_for_all_worker_to_be_ready).start()

            with ThreadPoolExecutor() as executor:
                for index in range(len(self.channels)):
                    profile_dir: str = self.profiles_dir + f"\\{temp_profiles[index]}"
                    wait_time: int = self.get_start_storm_wait_time(index, no_of_temp_profiles, self.slow_mode)

                    executor.submit(self.EachChannel, self.channels[index], profile_dir, wait_time)
                    sleep(0.2)  # Small delay to avoid instant spike of the cpu load

            environ.update({"BUSY": "0"})
            print("All threads completed")
    
        Thread(target=start_each_worker).start()
    
    def start_more_channels(self, channels: list[int]) -> None:
        
        def get_profiles() -> tuple[bool, list[str]]:
            count: int = 0
            available_profiles: list[str] = []
            for key, value in self.assigned_profiles.items():
                if value is None:
                    count += 1
                    available_profiles.append(key)

            return count >= len(channels), available_profiles[:len(channels)]

        enough_profiles, available_profiles = get_profiles()

        already_running_channels: list[int] = self.assigned_profiles.values()

        for channel in channels:
            if channel in already_running_channels:
                raise SystemError(f"Channel {channel} : {self.all_channels[str(channel)]['name']} is already running.")
        if not enough_profiles:
            raise SystemError("Not enough available profiles to start more channels.")
        
        def start_each_worker() -> None:            
            with ThreadPoolExecutor() as executor:
                for index in range(len(channels)):
                    print(index, len(available_profiles), channels[index], available_profiles[index], self.slow_mode)
                    profile_dir: str = self.profiles_dir + f"\\{available_profiles[index]}"
                    wait_time: int = self.get_start_storm_wait_time(index, len(available_profiles), self.slow_mode)

                    executor.submit(self.EachChannel, channels[index], profile_dir, wait_time)
                    sleep(0.2)
                    
                    
        Thread(target=start_each_worker).start()
            
        
        

        