from logging import Logger, getLogger

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from ..utils.exceptions import BrowserClosedError, ElementNotFound
from .BrowserAutomator import BrowserAutomator
        
logger: Logger = getLogger(f"streamstorm.{__name__}")

class Selenium(BrowserAutomator):
    __slots__: tuple[str, ...] = ('user_data_dir', 'background', 'driver')
    
    def __init__(self, user_data_dir: str, background: bool) -> None:
        self.user_data_dir: str = user_data_dir
        self.background: bool = background
        
    def go_to_page(self, url: str) -> None:
        self.driver.get(url)

    def find_element(self, by: str, value: str, wait_time: int = 15, just_available: bool = False, stale_count: int = 0) -> WebElement:
        if stale_count > 3:
            logger.error(f"Element not found: Stale Count Exceeded: {by} : {value}")
            raise ElementNotFound
        
        try:
            logger.debug(f"Looking for element: {by} : {value}")
            if just_available:
                element: WebElement = WebDriverWait(self.driver, wait_time).until(EC.visibility_of_element_located((by, value)))
            else:
                element: WebElement = WebDriverWait(self.driver, wait_time).until(EC.element_to_be_clickable((by, value)))
            
            logger.debug(f"Element found: {by} : {value}")
            
        except TimeoutException as e:
            logger.error(f"Element not found: {by} : {value}")
            raise ElementNotFound from e
        
        except StaleElementReferenceException:
            logger.error(f"Element not found: StaleElementReferenceException: Trying again: {by} : {value}")
            return self.find_element(by, value, wait_time=wait_time, just_available=just_available, stale_count=stale_count + 1)
        
        return element
    
    def find_elements(self, by: str, value: str, wait_time: int = 15) -> list[WebElement]:
        
        elements: list[WebElement] = []
        
        try:
            logger.debug(f"Looking for elements: {by} : {value}")
            elements: list[WebElement] = WebDriverWait(self.driver, wait_time).until(EC.presence_of_all_elements_located((by, value)))
            
        except TimeoutException as e:
            logger.error(f"Elements not found: {by} : {value}")
            raise ElementNotFound from e
        
        if not elements:
            raise ElementNotFound
        
        return elements


    def find_and_click_element(self, 
        by: str, 
        value: str, 
        element_name: str = "", 
        scroll: bool = True, 
        for_subscribe: bool = False, 
        for_profiles_init: bool = False, 
        just_available: bool = False) -> None:

        try:
            element: WebElement = self.find_element(by, value, wait_time=5 if for_profiles_init else 15, just_available=just_available)
            logger.debug(f"Element found: {element_name} : {by} : {value}")

            if scroll:
                self.driver.execute_script("arguments[0].scrollIntoView();", element)
                
            element.click()
            logger.debug(f"Element clicked: {element_name} : {by} : {value}")

        except (ElementNotInteractableException, ElementNotFound) as e:
            logger.error(f"Element not found: {element_name} : {by} : {value} : {e}")
            
            if not for_subscribe and not for_profiles_init:
                self.driver.close()
                raise BrowserClosedError from e
            
         
    def switch_to_frame(self, frame: WebElement = None, default: bool = False, name="") -> None:
        logger.debug("Switching to an iframe")      
        
        
        if default:
            logger.debug("Switching to default iframe")
            self.driver.switch_to.parent_frame()
            
        else:
            logger.debug(f"Switching to iframe: {name}")
            WebDriverWait(self.driver, 15).until(EC.frame_to_be_available_and_switch_to_it(frame))           
            
        logger.debug("Switched to iframe")
        
            
    def check_language_english(self) -> bool:
        html_tag: WebElement = self.find_element(By.TAG_NAME, "html")
        language: str = html_tag.get_attribute("lang")
        
        return language.startswith("en-") 
    
    
    def change_language(self):
        raise NotImplementedError
    
        
    async def open_browser(self):
        """
        No-op async method to satisfy the abstract base class. Not used in Selenium context.
        """
        return
    
    
    def type_and_enter(self, by: str, value: str, message: str, enter: bool = True) -> None:
        logger.debug(f"Typing message into field: '{message[:50]}{'...' if len(message) > 50 else ''}'")
        
        element: WebElement = self.find_element(by, value)
        element.send_keys(message)
        
        if enter: 
            element.send_keys(Keys.ENTER)        
            logger.debug("Message typed and Enter pressed")
        else:
            logger.debug("Message typed")
        
          
    
        
        
__all__: list[str] = ['Selenium']