from typing import Optional
from contextlib import suppress

from .UndetectedDrivers import UndetectedDrivers
from ..utils.cookies import get_cookies
from ..settings import settings

class CreateChannels(UndetectedDrivers):
    def __init__(self, logo_needed: bool, random_logo: bool) -> None:
        base_profile_dir: str = settings.environment_dir / "BaseProfile"
        
        super().__init__(str(base_profile_dir), custom_logo_needed=logo_needed and not random_logo)
        
        self.logo_needed: bool = logo_needed
        self.random_logo: bool = random_logo
        self.cookies: Optional[list] = get_cookies()
        
    def start(self, channels: list):
        self.initiate_base_profile(self.cookies)
        self.youtube_login(for_create_channels=True, logged_in=self.cookies is not None)

        unsuccessful_creations: list = []

        for channel in channels:
            created: bool = self.create_channel(channel["name"], self.logo_needed, self.random_logo, channel["uri"])

            if not created:
                unsuccessful_creations.append(channel["name"])
                
        with suppress(Exception): 
            self.driver.close()

        return unsuccessful_creations or None
            