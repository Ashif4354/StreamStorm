from abc import ABC, abstractmethod

class BrowserAutomator(ABC):

    @abstractmethod
    def open_browser(self) -> None:
        """Open a browser and navigate to the specified URL."""
        pass

    @abstractmethod
    def go_to_page(self, url: str) -> None:
        """Navigate to the specified URL."""
        pass

    @abstractmethod
    def find_and_click_element(self, *args, **kwargs) -> None:
        """Find an element and click it."""
        pass

    @abstractmethod
    def find_element(self, *args, **kwargs) -> None:
        """Find an element on the page."""
        pass

    @abstractmethod
    def type_and_enter(self, *args, **kwargs) -> None:
        """Type a message into a text field and press enter."""
        pass
    
    @abstractmethod
    def check_language_english(self) -> None:
        """Check if the language of the page is English."""
        pass
    
    @abstractmethod
    def change_language(self) -> None:
        """Change the language of the browser to English."""
        pass
    

__all__: list[str] = ['BrowserAutomator']
