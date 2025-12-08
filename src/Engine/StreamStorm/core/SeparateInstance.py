from contextlib import suppress
from asyncio import sleep
from logging import getLogger, Logger
from typing import Optional
from playwright.async_api._generated import Locator
from playwright._impl._errors import TargetClosedError

from ..utils.exceptions import BrowserClosedError
from .Playwright import Playwright

logger: Logger = getLogger(f"streamstorm.{__name__}")

class SeparateInstance(Playwright):
    __slots__: tuple[str, ...] = ('channel_name', 'index')

    def __init__(
        self,
        index: int,
        user_data_dir: str = '',
        background: bool = True
    ) -> None:
        super().__init__(user_data_dir, background)
        
        self.index: int = index
        self.__instance_alive: bool = True
        self.__logged_in: Optional[bool] = None
        
        
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

            await sleep(3)
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
            if not self.browser.browser.is_connected(): # test 1
                self.__instance_alive = False
                logger.info(f"[{self.index}] [{self.channel_name}] : ##### StreamStorm instance marked as dead by: browser.browser.is_connected")

        except TargetClosedError as _:
            self.__instance_alive = False
            logger.info(f"[{self.index}] [{self.channel_name}] : ##### StreamStorm instance marked as dead by: TargetClosedError")

        except Exception as e:
            logger.error(f"[{self.index}] [{self.channel_name}] : Error occurred while checking StreamStorm instance: {type(e).__name__}, {e}")
            logger.info(f"[{self.index}] [{self.channel_name}] : ##### StreamStorm instance marked as dead by: Exception")
            self.__instance_alive = False
        
        return self.__instance_alive


    async def __click_channel(self, index: int) -> None:
        logger.debug(f"[{self.index}] [{self.channel_name}] Clicking on channel at position {index}")
        await self.find_and_click_element(
            f"//*[@id='contents']/ytd-account-item-renderer[{index}]",
            "channel_element"
        )
        
        with suppress(Exception):
            await self.find_and_click_element(
                '//*[@id="confirm-button"]//button',
                "OK button for brand account",
                True
            )

    async def subscribe_to_channel(self) -> None:
        await self.find_and_click_element(
            "//div[@id='subscribe-button']/*//button[.//span[text()='Subscribe']]",
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
        
    async def start_instance(self):
        ...
        
        




__all__: list[str] = ['SeparateInstance']
