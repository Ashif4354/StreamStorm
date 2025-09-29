from os.path import dirname, normpath, join
from json import dump
from time import sleep
from warnings import deprecated
from undetected_chromedriver import Chrome
from logging import getLogger, Logger
from contextlib import suppress

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException, ElementNotInteractableException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

from .Selenium import Selenium

logger: Logger = getLogger(f"streamstorm.{__name__}")

class UndetectedDrivers(Selenium):
    __slots__: tuple[str, ...] = ('base_profile_dir', 'youtube_login_url', 'config_json_path')
    
    def __init__(self, base_profile_dir: str) -> None:
        self.base_profile_dir: str = base_profile_dir
        self.youtube_login_url: str = "https://accounts.google.com/ServiceLogin?service=youtube"
        self.config_json_path: str = join(dirname(normpath(self.base_profile_dir)), "config.json")
        
        super().__init__(base_profile_dir, background=False)

    def initiate_config_json(self, no_of_channels: int = 0, channels: dict[int, dict[str, str]] = None) -> None:

        data: dict = {
            "no_of_channels": no_of_channels,
            "channels": channels or {}
        }
        
        try:
            with open(self.config_json_path, "w", encoding="utf-8") as file:
                dump(data, file, indent=4)
        except Exception as e:
            raise RuntimeError(f"Failed to create config.json: {e}") from e
         
    @deprecated("Using user installed Chrome now.")
    def get_browser_path(self) -> str:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            chromium_executable: str = p.chromium.executable_path
            return chromium_executable


    def initiate_base_profile(self) -> None:

        self.driver = Chrome(
            user_data_dir=self.base_profile_dir,
        )

        logger.debug(f"Browser PID: {self.driver.browser_pid}")

    def get_total_channels(self) -> None:
        
        with suppress(NoSuchElementException, ElementNotInteractableException):
            # select first channel if popup appears
            self.find_and_click_element(By.XPATH, "//ytd-popup-container//*[@id='contents']/ytd-account-item-renderer[1]", for_profiles_init=True)
        
        self.find_and_click_element(By.XPATH, '//*[@id="avatar-btn"]')
        self.find_and_click_element(By.XPATH, "//*[text()='Switch account']")

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='submenu']//*[@id='container']//*[@id='contents']//*[@id='contents']/ytd-account-item-renderer")))

        channels_list: list[WebElement] = self.driver.find_elements(By.XPATH, "//*[@id='submenu']//*[@id='container']//*[@id='contents']//*[@id='contents']/ytd-account-item-renderer")
        
        channels: dict[int, dict[str, str]] = {}

        for index in range(len(channels_list)):
            try:
                self.driver.execute_script("arguments[0].scrollIntoView();", channels_list[index])
                
                channel_name_element: WebElement = channels_list[index].find_element(By.ID, "channel-title")
                channel_name: str = channel_name_element.text
                
                channel_logo_element: WebElement = channels_list[index].find_element(By.ID, "img")
                channel_logo_url: str = channel_logo_element.get_attribute("src")
                
                channels[index + 1] = {
                    "name": channel_name,
                    "logo": channel_logo_url
                }
                
            except NoSuchElementException:
                continue
        total_channels: int = len(channels_list)

        if total_channels == 0:
            raise SystemError("No YouTube channels found. Add at least one channel to your YouTube Account.")
        
        self.initiate_config_json(total_channels, channels)

    def youtube_login(self, for_create_channels: bool = False) -> None:
        self.go_to_page(self.youtube_login_url)
        logged_in: bool = False

        default_tab: str = self.driver.current_window_handle
        try:
            while not logged_in:
                tabs: list[str] = self.driver.window_handles
                
                for tab in tabs:
                    if tab != default_tab:
                        self.driver.switch_to.window(tab)
                        self.driver.close()
                        self.driver.switch_to.window(default_tab)
            
                if not self.driver.current_url.startswith("https://accounts.google.com/v3/signin"):
                    self.driver.get(self.youtube_login_url)
                
                if self.driver.current_url.startswith("https://www.youtube.com/"):
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.ID, "avatar-btn"))
                        )
                        logger.info("Youtube login successful")
                        
                        if not for_create_channels:
                            self.get_total_channels()                            
                            self.driver.close()
                            
                        sleep(2)

                        logged_in = True
                    except NoSuchElementException:
                        self.driver.get(self.youtube_login_url)
                        
        except (NoSuchWindowException, AttributeError) as e:
            raise RuntimeError("The Browser window was closed or not found. Try again.") from e
        



__all__: list[str] = ["UndetectedDrivers"]
