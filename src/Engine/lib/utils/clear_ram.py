from subprocess import Popen
from warnings import deprecated
from platform import system

from ..settings import settings

from logging import getLogger, Logger

logger: Logger = getLogger(f"streamstorm.{__name__}")

@deprecated("Not used anymore.")
def clear_ram() -> None:
    
    if system() != "Windows":
        return
    
    rammap_path: str = str(settings.root / "RAMMap.exe")
    
    try:
        Popen(
            [
                rammap_path,
                "-Ew", # 
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