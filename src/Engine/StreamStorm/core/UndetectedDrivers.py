from os.path import dirname, normpath, join
from json import dump
from random import randint
from time import sleep
from warnings import deprecated
from undetected_chromedriver import Chrome
from logging import getLogger, Logger
from contextlib import suppress
with suppress(KeyError): # 
    from pyautogui import write as pyautogui_write, press as pyautogui_press
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
        logger.debug(f"Base profile directory: {self.base_profile_dir}")
        
        self.youtube_login_url: str = "https://accounts.google.com/ServiceLogin?service=youtube"
        self.config_json_path: str = join(dirname(normpath(self.base_profile_dir)), "data.json")
        
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
            logger.error(f"Failed to create data.json: {e}")
            raise RuntimeError(f"Failed to create data.json: {e}") from e
         
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
            self.find_and_click_element(By.XPATH, "//ytd-popup-container//*[@id='contents']/ytd-account-item-renderer[1]", element_name="First channel in popup", for_profiles_init=True)
        
        self.find_and_click_element(By.XPATH, '//*[@id="avatar-btn"]', element_name="Avatar button")
        
        self.find_and_click_element(By.XPATH, "//*[text()='Switch account']", element_name="Switch account button")

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
                
            except NoSuchElementException as e:
                logger.error(f"Error occurred while getting channel {index}: {e}")
                
                continue
            
        total_channels: int = len(channels_list)

        if total_channels == 0:
            raise SystemError("No YouTube channels found. Add at least one channel to your YouTube Account.")
        
        self.initiate_config_json(total_channels, channels)
        
        
    def create_channel(self, name: str, logo: bool = True, random_logo: bool = False, logo_uri: str = None) -> bool:
        # sourcery skip: extract-method
        logger.info(f"Creating channel: {name}")
        self.go_to_page("https://www.youtube.com/account")

        self.find_and_click_element(By.XPATH, '//*[@id="options"]//*/a[text()="Add or manage your channel(s)"]', element_name="Add or manage your channel(s) button")
        self.find_and_click_element(By.XPATH, '//*[@id="contents"]/ytd-button-renderer/yt-button-shape/a[contains(., "Create a channel")]', element_name="Create a channel button", scroll=False)

        try:
            self.type_and_enter(By.XPATH, '//*[@id="input-2"]/input', name, enter=False)
        except ElementNotInteractableException:
            try:
                self.type_and_enter(By.XPATH, '//*[@id="input-1"]/input', name, enter=False)
            except ElementNotInteractableException:
                return False


        if logo:
            self.find_and_click_element(By.XPATH, '//button[@aria-label="Select picture"]', element_name="Select picture button")

            last_iframe: WebElement = self.find_element(By.XPATH, '//iframe[@aria-modal="true"]')

            self.switch_to_frame(last_iframe, name="Select picture iframe")

            if random_logo:
                rand_num: int= randint(1, 3)
                self.find_and_click_element(By.XPATH, f'//div[@aria-label="Choose picture"]//c-wiz[2]//button[{rand_num}]/img', element_name="Random picture", just_available=True)

                self.find_and_click_element(By.XPATH, '(//button[contains(., "Done")])[1]', element_name="Done button")  

            else:                
                self.find_and_click_element(By.XPATH, '(//button[contains(., "From computer")])[last()]', element_name="From computer button")

                self.find_and_click_element(By.XPATH, '(//button[contains(., "Upload from computer")])[last()]', element_name="Upload from computer button")
                sleep(1)

                pyautogui_write(logo_uri)
                sleep(3)
                pyautogui_press("enter")               

                self.find_and_click_element(By.XPATH, '(//button[contains(., "Done")])[last()]', element_name="Done button")   

            self.switch_to_frame(default=True)         

        self.find_and_click_element(By.XPATH, '//button[@aria-label="Create channel"]', element_name="Create channel button")       

        count: int = 0
        while self.driver.current_url == "https://www.youtube.com/account":
            sleep(1)

            with suppress(Exception):
                logger.debug(f"FInding failed to create channel error text count: {count}")
                self.find_element(By.XPATH, '//yt-formatted-string[contains(text(), "Failed to create channel.")]', just_available=True, wait_time=2)
                return False
            
            count += 1
            if count == 30:
                return False

        return True
        

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
                        
                        english: bool = self.check_language_english()  
                              
                        if not english: 
                            self.driver.get("https://www.youtube.com/account?hl=en-US&persist_hl=1")
                            
                        logger.info("Youtube login successful")
                        logged_in = True
                        
                        if not for_create_channels:
                            self.get_total_channels()                            
                            self.driver.close()
                            
                            sleep(2)

                        
                    except NoSuchElementException:
                        
                        self.driver.get(self.youtube_login_url)
                        
        except (NoSuchWindowException, AttributeError) as e:
            logger.error(f"Error occurred while logging in: The Browser window was closed or not found: {e}")
            
            raise RuntimeError("The Browser window was closed or not found. Try again.") from e
        


__all__: list[str] = ["UndetectedDrivers"]