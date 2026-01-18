from typing import Any
from asyncio import to_thread, sleep
from psutil import cpu_percent, virtual_memory
from logging import getLogger, Logger

from ..socketio.sio import sio

logger: Logger = getLogger(f"streamstorm.{__name__}")

def get_system_metrics() -> dict[str, Any]:
    mem: Any = virtual_memory()
    free_ram_mb: int = int(mem.available / (1024**2))  # MB without decimals

    return {
        "cpu_percent": str(cpu_percent(interval=None)),
        "ram_percent": str(mem.percent),
        "used_ram_gb": str(mem.used / (1024**3)),
        "free_ram_percent": str((mem.available * 100) / mem.total),
        "free_ram_gb": str(mem.available / (1024**3)),
        "free_ram_mb": str(free_ram_mb),
    }


async def emit_system_metrics() -> None:
    while True:
        try:
            system_metrics: dict[str, Any] = await to_thread(get_system_metrics)
            await sio.emit("system_metrics", system_metrics, room="streamstorm")
        except Exception as e:
            logger.error(f"Error occurred in emit_system_metrics: {e}")
        finally:
            await sleep(2)
            