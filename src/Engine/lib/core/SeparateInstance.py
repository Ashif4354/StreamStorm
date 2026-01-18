from asyncio import (
    sleep as asyncio_sleep,
    TimeoutError as AsyncTimeoutError,
    CancelledError,
    Task,
    create_task as asyncio_create_task
)
from logging import getLogger, Logger
from typing import Optional
from http.client import RemoteDisconnected
from urllib3.exceptions import ProtocolError, ReadTimeoutError
from random import choice
from contextlib import suppress

from playwright.async_api._generated import Locator
from playwright._impl._errors import TargetClosedError
from playwright.async_api import (
    Error as PlaywrightError, 
    TimeoutError as PlaywrightTimeoutError,
)

from ..utils.exceptions import BrowserClosedError, ElementNotFound
from .Playwright import Playwright
from .StormContext import StormContext
from ..socketio.sio import sio

logger: Logger = getLogger(f"streamstorm.{__name__}")

class SeparateInstance(Playwright):
    __slots__: tuple[str, ...] = (
        'channel_name', 'index', 'wait_time', 
        'should_wait', 'profile_dir_name', 'context',
        '_SeparateInstance__logged_in', '_SeparateInstance__sleep_tasks'
    )

    def __init__(
        self,
        index: int,
        user_data_dir: str = '',
        wait_time: float = 0,
        channel_name: str = '',
        cookies: list[dict] | None = None,
        storm_context: StormContext | None = None
    ) -> None:
        super().__init__(user_data_dir, storm_context.background, cookies, index, channel_name)
        
        self.index: int = index
        self.profile_dir_name: str = user_data_dir.split("\\")[-1]  # Profile dir name : Used in StormRouter.py for killing instance
        self.__logged_in: Optional[bool] = None
        self.__sleep_tasks: list[Task] = []
        self.wait_time: float = wait_time
        self.channel_name: str = channel_name
        self.should_wait: bool = True
        self.context: StormContext | None = storm_context

    def __repr__(self) -> str:
        return f"Instance(index={self.index}, channel_name={self.channel_name}, wait_time={self.wait_time})"
        
        
    async def change_language(self):
        await self.go_to_page("https://www.youtube.com/account?hl=en-US&persist_hl=1")             


    async def login(self) -> bool:        
        logger.debug(f"[{self.index}] [{self.channel_name}] Starting login process...")

        try:
            logger.debug(f"[{self.index}] [{self.channel_name}] Opening browser...")
            await self.open_browser()
            
            await self.go_to_page("https://www.youtube.com/account") # We are going to account page because it loads faster than the main page
            
            english: bool = await self.check_language_english()            
            
            if not english:
                await self.change_language()
                
            await self.find_and_click_element('//*[@id="avatar-btn"]', 'avatar_button') # Click on avatar button
            
            
            await self.find_and_click_element("//*[text()='Switch account']", 'switch_account_button') # Click on switch account button

            await asyncio_sleep(3)
            logger.debug(f"[{self.index}] [{self.channel_name}] Selecting channel {self.index}...")
            await self.__click_channel(self.index)

            logger.debug(f"[{self.index}] [{self.channel_name}] Login completed successfully")
            
            self.__logged_in = True
            return True
        
        except BrowserClosedError as _:  
            logger.error(f"[{self.index}] [{self.channel_name}] Login failed due to browser closure")
            
            self.__logged_in = False
            return False

        
    async def is_instance_alive(self) -> bool:
        
        if self.__logged_in is None:
            return True
        
        try:
            if not self.browser_context.browser.is_connected(): # test 1
                self._is_alive = False
                logger.debug(f"[{self.index}] [{self.channel_name}] : ##### StreamStorm instance marked as dead by: browser.browser.is_connected")

        except TargetClosedError as _:
            self._is_alive = False
            logger.debug(f"[{self.index}] [{self.channel_name}] : ##### StreamStorm instance marked as dead by: TargetClosedError")

        except Exception as e:
            logger.error(f"[{self.index}] [{self.channel_name}] : Error occurred while checking StreamStorm instance: {type(e).__name__}, {e}")
            logger.debug(f"[{self.index}] [{self.channel_name}] : ##### StreamStorm instance marked as dead by: Exception")
            self._is_alive = False
        
        try:

            if not self._is_alive and len(self.__sleep_tasks) > 0:
                for task in self.__sleep_tasks:
                    if not task.done():
                        logger.debug(f"[{self.index}] [{self.channel_name}] Canceling sleep task: {task.get_name()}")
                        task.cancel()

                self.__sleep_tasks.clear() 

        except Exception as e:
            logger.error(f"[{self.index}] [{self.channel_name}] : Error occurred while canceling sleep tasks: {type(e).__name__}, {e}")
                              
        return self._is_alive


    async def __click_channel(self, index: int) -> None:
        logger.debug(f"[{self.index}] [{self.channel_name}] Clicking on channel at position {index}")
        brand_account: bool = await self.find_and_click_element(
            f"//*[@id='contents']/ytd-account-item-renderer[{index}]",
            "channel_element"
        )
        if brand_account:
            await self.find_and_click_element(
                '//*[@id="confirm-button"]//button',
                "OK button for brand account",
                True
            )


    async def subscribe_to_channel(self, channel_fetched: bool) -> None:
        await self.find_and_click_element(
            "//button[.//div[text()='Subscribe']]" if channel_fetched else "//button[.//span[text()='Subscribe']]",
            "subscribe_button",
            True
        )           
        logger.debug(f"[{self.index}] [{self.channel_name}] Subscribe action completed")

        
    async def __get_chat_field(self) -> Locator:
        chat_field: Locator = await self.find_element("//yt-live-chat-text-input-field-renderer//div[@id='input']", "chat_field")
        return chat_field


    async def send_message(self, message: str) -> None:
        logger.debug(f"[{self.index}] [{self.channel_name}] Getting chat field and sending message: '{message}'")
        chat_field: Locator = await self.__get_chat_field() # We get chat_field repeatedly to overcome potential stale element issues or DOM changes
        await self.type_and_enter(chat_field, message)
        logger.debug(f"[{self.index}] [{self.channel_name}] Message sent to chat field")


    async def emit_instance_status(self, index: int, status: int) -> None:
        str_index: str = str(index)
        self.context.all_channels[str_index]["status"] = status
        await sio.emit("instance_status", {"instance": str_index, "status": str(status)}, room="streamstorm")

    async def sleep(self, duration: float) -> None:
        try:
            await asyncio_sleep(duration)
        except CancelledError:
            logger.debug(f"[{self.index}] [{self.channel_name}] Sleep task cancelled")



    async def start(self) -> None:        
        instance_started: bool = False
        exit_reason: str = "Normal completion"
        
        try:            
            await self.emit_instance_status(self.index, 1)  # 1 = Getting Ready

            self.context.assigned_profiles[self.profile_dir_name] = self.index

            logger.info(f"[{self.index}] [{self.channel_name}] Assigned profile {self.profile_dir_name}")

            self.context.each_channel_instances.append(self)
            instance_started = True
            
            logger.info(f"[{self.index}] [{self.channel_name}] Attempting login...")
            logged_in: bool = await self.login()
            
            self.context.run_stopper_event.set()  # Set the event to signal that stopper can check for instance errors
            logger.debug(f"[{self.index}] [{self.channel_name}] Run stopper event set")
            
            if not logged_in:
                logger.debug(f"[{self.index}] [{self.channel_name}] Login failed - removing from instances")
                
                self.context.total_instances -= 1
                
                logger.error(f"[{self.index}] [{self.channel_name}] : Login failed")
                exit_reason = "Login failed"
                return

            logger.info(f"[{self.index}] [{self.channel_name}] Login successful")

            if self.context.subscribe[0]:
                logger.debug(f"[{self.index}] [{self.channel_name}] Navigating to subscribe URL: {self.context.video_url}")
                
                await self.go_to_page(self.context.target_channel[0])
                await self.subscribe_to_channel(self.context.target_channel[1])
                
                logger.info(f"[{self.index}] [{self.channel_name}] Subscription attempt completed")

            await self.page.set_viewport_size({"width": 500, "height": 900})
            logger.info(f"[{self.index}] [{self.channel_name}] Navigating to chat URL: {self.context.chat_url}")
            await self.go_to_page(self.context.chat_url)
            
            self.context.ready_to_storm_instances += 1
            logger.info(f"[{self.index}] [{self.channel_name}] : Ready To Storm")
            await self.emit_instance_status(self.index, 2)  # 2 = Ready

            if self.context.subscribe[1]:
                logger.info(f"[{self.index}] [{self.channel_name}] Waiting {self.context.subscribe_and_wait_time}s after subscription")
                
                sleep_task = asyncio_create_task(self.sleep(self.context.subscribe_and_wait_time), name="subscription_wait")
                self.__sleep_tasks.append(sleep_task)
                await sleep_task
                
                with suppress(Exception):
                    self.__sleep_tasks.remove(sleep_task)
                 
                
            logger.debug(f"[{self.index}] [{self.channel_name}] Waiting for ready event...")
            await self.context.ready_event.wait() # Wait for the ready event to be set before starting the storming
            
            logger.debug(f"[{self.index}] [{self.channel_name}] Starting storm loop with {self.wait_time}s initial delay")
            await self.emit_instance_status(self.index, 3)  # 3 = Storming

            while True:
                await self.context.pause_event.wait()
                if self.should_wait:

                    sleep_task = asyncio_create_task(self.sleep(self.wait_time), name="storming_wait")
                    self.__sleep_tasks.append(sleep_task)
                    await sleep_task
                    
                    with suppress(Exception):
                        self.__sleep_tasks.remove(sleep_task)
                    
                    self.should_wait = False
        
                # input()
                selected_message = choice(self.context.messages)
                logger.debug(f"[{self.index}] [{self.channel_name}] Sending message: '{selected_message}'")
                
                try:
                    await self.send_message(selected_message)
                    
                    async with self.context.message_counter_lock:
                        self.context.message_count += 1
                        
                    logger.debug(f"[{self.index}] [{self.channel_name}] Message sent successfully")
                    
                except (BrowserClosedError, ElementNotFound, TargetClosedError):
                    logger.debug(f"[{self.index}] [{self.channel_name}] : ##### Browser/element error - cleaning up instance")
                    logger.error(f"[{self.index}] [{self.channel_name}] : Error in finding chat field")
                    exit_reason = "Browser/element error - chat field not found"
                    break
                    
                except Exception as e:
                    logger.error(f"[{self.index}] [{self.channel_name}] : New Error ({type(e).__name__}): {e}")
                    exit_reason = f"Unexpected error: {type(e).__name__}"
                    break
                
                logger.debug(f"[{self.index}] [{self.channel_name}] Sleeping for {self.context.slow_mode}s before next message")
                
                sleep_task = asyncio_create_task(self.sleep(self.context.slow_mode), name="slow_mode")
                self.__sleep_tasks.append(sleep_task)
                await sleep_task

                with suppress(Exception):
                    self.__sleep_tasks.remove(sleep_task)

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
            logger.error(f"[{self.index}] [{self.channel_name}] : Error: {e}")
            exit_reason = f"Connection/browser error: {type(e).__name__}"
        
        finally:
            # Guaranteed cleanup on all exit paths
            self.context.assigned_profiles[self.profile_dir_name] = None
            
            if instance_started:
                with suppress(ValueError):
                    self.context.each_channel_instances.remove(self)
                    logger.debug(f"[{self.index}] [{self.channel_name}] : Removed from instances")
            
            await self.emit_instance_status(self.index, 0)  # 0 = Dead
            await self.close_browser(reason=exit_reason)
            logger.info(f"[{self.index}] [{self.channel_name}] : Instance cleanup completed")




__all__: list[str] = ['SeparateInstance']
