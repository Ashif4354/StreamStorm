from logging import Formatter, Logger, getLogger, DEBUG, INFO, FileHandler, NullHandler, Handler, LogRecord
from logging.handlers import QueueHandler, QueueListener
from platformdirs import user_data_dir
from pathlib import Path
from queue import Queue
from rich.logging import RichHandler
from atexit import register as atexit_register
from datetime import datetime
from asyncio import AbstractEventLoop, run_coroutine_threadsafe

from .GetIstTime import get_ist_time
from ..settings import settings
from ..api.validation import StormData
from ..socketio.sio import sio
from ..core.StreamStorm import StreamStorm

_event_loop: AbstractEventLoop | None = None

def set_logging_loop(loop: AbstractEventLoop) -> None:
    global _event_loop
    _event_loop = loop

class SocketIOHandler(Handler):
    def emit(self, record: LogRecord) -> None:
        if _event_loop is None or _event_loop.is_closed():
            # No loop yet, just ignore
            return
        
        level: str = record.levelname
        if level == "DEBUG":
            return
        
        time: str = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")

        try:
            msg: str = self.format(record)
            run_coroutine_threadsafe(self._emit_async(msg, level, time), _event_loop)

        except Exception:
            self.handleError(record)

    async def _emit_async(self, msg: str, level: str, time: str) -> None:
        await sio.emit("log", {"message": msg, "level": level, "time": time}, room="streamstorm")   
        

class CustomLogger:
    __slots__: tuple[str, ...] = ('logging_dir', 'logger', 'queue_handler')
    
    log_queue: Queue = Queue(-1)
    listener: QueueListener | None = None
    
    def __init__(self, for_history: bool = False) -> None:
        self.logging_dir: Path = Path(user_data_dir("StreamStorm", "DarkGlance")) / "logs"
        self.logging_dir.mkdir(parents=True, exist_ok=True)
        
        if not for_history:
            self.queue_handler: Handler = QueueHandler(self.log_queue)
            
            CustomLogger.listener = QueueListener(self.log_queue, self.__get_console_handler(), self.__get_file_handler(), self.__get_socketio_handler())
            CustomLogger.listener.start()
        
            atexit_register(CustomLogger.listener.stop)

    def __get_console_handler(self) -> Handler:
        
        env: str = settings.env
        handler: Handler = NullHandler()

        if env == "development":
            handler = RichHandler(
                rich_tracebacks=True,
                markup=False,
                show_time=True,
                show_path=True,
                show_level=True,
                enable_link_path=True
            )

        return handler
    
    def __get_file_handler(self) -> FileHandler:       
        # sourcery skip: class-extract-method
        
        log_file: Path = self.__touch_log_file(f"log - {get_ist_time()}.log")
        settings.log_file_path = str(log_file)

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
    
    def __get_socketio_handler(self) -> SocketIOHandler:
        
        return SocketIOHandler()
    
    def __setup_logging(self, name: str) -> None:
        
        logger: Logger = getLogger(name)
        logger.setLevel(DEBUG)
        logger.addHandler(self.queue_handler)
        logger.propagate = False
        
    def __touch_log_file(self, file_name) -> Path:
        
        log_file: Path = self.logging_dir / file_name
        log_file.touch(exist_ok=True)
        
        return log_file

    def setup_streamstorm_logging(self) -> None:
        
        self.__setup_logging("streamstorm")

    def setup_fastapi_logging(self) -> None:

        self.__setup_logging("fastapi")

    def setup_fastmcp_logging(self) -> None:

        self.__setup_logging("mcpapp")

    def setup_history_logger(self) -> None:

        log_file: Path = self.__touch_log_file("History.log")
        
        formatter: Formatter = Formatter(
            "============================================================\n%(message)s"
        )
        
        handler: FileHandler = FileHandler(
            log_file,
            mode="a",
            encoding="utf-8"
        )
        
        handler.setFormatter(formatter)
        
        logger: Logger = getLogger("history")
        logger.setLevel(INFO)
        logger.addHandler(handler)
        logger.propagate = False
        
    def log_to_history(self, data: StormData, remarks: str = "No remarks") -> None:
        if settings.env == "test":
            return
        
        logger: Logger = getLogger("history")
        
        date_time: str = get_ist_time()
        
        message_str: str = "\n".join([f"{k}: {v}" for k, v in data.__dict__.items()]) + f"\n\nRemarks: {remarks}\n"
              
        message_str = f"Date Time: {date_time}\n\n{message_str}\n"
        
        logger.info(message_str)
        

custom_logger: CustomLogger = CustomLogger()

__all__: list[str] = ["custom_logger"]