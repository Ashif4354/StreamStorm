from tempfile import gettempdir

from .UndetectedDrivers import UndetectedDrivers


class CreateChannels(UndetectedDrivers):
    def __init__(self, channels: list[str]) -> None:
        
        self.channels: list[str] = channels
        super().__init__(gettempdir())
        
        
    