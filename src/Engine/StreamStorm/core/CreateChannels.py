from tempfile import gettempdir
from pathlib import Path
from contextlib import suppress

from .UndetectedDrivers import UndetectedDrivers

class CreateChannels(UndetectedDrivers):
    def __init__(self, logo_needed: bool, random_logo: bool) -> None:
        temp_profile_dir: Path = Path(gettempdir()) / "ss_temp_profile"
        
        super().__init__(str(temp_profile_dir))
        
        self.logo_needed: bool = logo_needed
        self.random_logo: bool = random_logo
        
    def start(self, channels: list):
        
        self.initiate_base_profile()
        self.youtube_login(for_create_channels=True)

        unsuccessful_creations: list = []

        for channel in channels:
            created: bool = self.create_channel(channel["name"], self.logo_needed, self.random_logo, channel["uri"])

            if not created:
                unsuccessful_creations.append(channel["name"])
                
        with suppress(Exception): 
            self.driver.close()

        return unsuccessful_creations or None
            