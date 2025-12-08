from subprocess import Popen
from platform import system
from ..config.config import CONFIG

from logging import getLogger, Logger

logger: Logger = getLogger(f"streamstorm.{__name__}")

def clear_ram() -> None:
    
    if system() != "Windows":
        return
    
    rammap_path: str = CONFIG['ROOT'] / "RAMMap.exe"
    
    try:
        Popen(
            [
                rammap_path,
                "-Ew",
                # "-Es",
                # "-Em",
                # "-Et",
                # "-E0",            
            ],
            shell=False,
            stdout=None,
            stderr=None,
        )
    except FileNotFoundError:
        logger.error("RAMMap.exe not found!")
    except PermissionError:
        logger.error("Permission denied while trying to run RAMMap.exe.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


__all__: list[str] = ["clear_ram"]