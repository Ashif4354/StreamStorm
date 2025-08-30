from logging import Formatter, Logger, getLogger, DEBUG, FileHandler, StreamHandler, NullHandler, Handler
from logging.handlers import QueueHandler, QueueListener
from platformdirs import user_data_dir
from pathlib import Path
from queue import Queue
from rich.logging import RichHandler
from atexit import register as atexit_register

from .GetIstTime import get_ist_time
from config import CONFIG

class CustomLogger:
    __slots__: tuple[str, ...] = ('logging_dir', 'logger')
    
    log_queue: Queue = Queue(-1)
    listener: QueueListener | None = None
    
    def __init__(self):
        self.logging_dir: Path = Path(user_data_dir("StreamStorm", "DarkGlance")) / "logs"

    def __get_console_handler(self) -> Handler:
        
        env: str = CONFIG.get("ENV")
        handler: Handler = NullHandler()

        if env == "production":
            
            # formatter: Formatter = Formatter(
            #     "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            #     datefmt="%m/%d/%y %H:%M:%S"
            # )

            # handler: Handler = StreamHandler()
            # handler.setFormatter(formatter)
            
            pass # No console handler is required in production
            
        elif env == "development":           

            handler: Handler = RichHandler(
                rich_tracebacks=True,
                markup=False,
                show_time=True,
                show_path=True,
                show_level=True,
                enable_link_path=True
            )
        
        
        
        return handler
    
    def __get_file_handler(self) -> FileHandler:
        
        self.logging_dir.mkdir(parents=True, exist_ok=True)
        
        log_file: Path = self.logging_dir / f"log - {get_ist_time()}.log"
        log_file.touch(exist_ok=True)

        file_formatter: Formatter = Formatter(
            "%(asctime)s [%(name)s: %(lineno)d] %(levelname)s: %(message)s"
        )
        
        handler: FileHandler = FileHandler(
            log_file,
            mode="a",
            encoding="utf-8"
        )
        
        handler.setFormatter(file_formatter)
        
        return handler

    def setup_streamstorm_logging(self) -> None:
        queue_handler = QueueHandler(self.log_queue)
        
        self.logger: Logger = getLogger("streamstorm")
        self.logger.setLevel(DEBUG)
        self.logger.addHandler(queue_handler)
        self.logger.propagate = False

        CustomLogger.listener = QueueListener(self.log_queue, self.__get_console_handler(), self.__get_file_handler())
        CustomLogger.listener.start()
        
        atexit_register(CustomLogger.listener.stop)

    def setup_fastapi_logging(self) -> None:
        queue_handler = QueueHandler(self.log_queue)

        self.logger: Logger = getLogger("fastapi")
        self.logger.setLevel(DEBUG)
        self.logger.addHandler(queue_handler)
        self.logger.propagate = False

        CustomLogger.listener = QueueListener(self.log_queue, self.__get_console_handler(), self.__get_file_handler())
        CustomLogger.listener.start()


