from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

from .Selenium import Selenium

class SeparateAccount(Selenium):
    def __init__(
        self,
        url: str,
        chat_url: str,
        messages: list[str] = ["Hello", "Hi"],
        index: int = 0,
        user_data_dir: str = '',
        driver_path: str = '',
        browser: str = 'edge',
        background: bool = True
    ) -> None:
        super().__init__(user_data_dir, driver_path, browser, background)
        
        self.url: str = url
        self.chat_url: str = chat_url
        self.messages: list[str] = messages
        self.index: int = index
           
        
    def login(self) -> None:
        
        self.open_browser()
        self.go_to_page("https://www.youtube.com")
        
        self.find_and_click_element(By.XPATH, '//*[@id="avatar-btn"]') # Click on avatar button
        self.find_and_click_element(By.XPATH, "//*[text()='Switch account']") # Click on switch account button
        
        sleep(3)
        
        self.__click_account(self.index)

    
    def __click_account(self, index: int) -> None:
        
        self.find_and_click_element(
            By.XPATH,
            f"//*[@id='contents']/ytd-account-item-renderer[{index}]"
        )

    def subscribe_to_channel(self) -> None:
                    
        self.find_and_click_element(
            By.XPATH,
            "//div[@id='subscribe-button']/*//button[.//span[text()='Subscribe']]",
            False
        )
        
            
        
    def __get_chat_field(self) -> WebElement:
        chat_field: WebElement = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, "//yt-live-chat-text-input-field-renderer//div[@id='input']")))
        
        return chat_field
    
    def send_message(self, message: str) -> None:
        
        chat_field: WebElement = self.__get_chat_field()
        self.type_and_enter(chat_field, message)
        
        




__all__: list[str] = ['SeparateAccount']