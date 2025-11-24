from typing import Any
from asyncio import to_thread, sleep
from contextlib import suppress
from psutil import cpu_percent, virtual_memory

from ..socketio.sio import sio

def get_system_metrics() -> dict[str, Any]:
    mem: Any = virtual_memory()
    free_ram_mb: int = int(mem.available / (1024**2))  # MB without decimals

    return {
        "cpu_percent": str(cpu_percent(interval=None)),
        "ram_percent": str(mem.percent),
        "ram_gb": str(mem.used / (1024**3)),
        "free_ram_percent": str((mem.available * 100) / mem.total),
        "free_ram_gb": str(mem.available / (1024**3)),
        "free_ram_mb": str(free_ram_mb),
    }


async def emit_system_metrics() -> None:
    while True:
        with suppress(Exception):
            system_metrics: dict[str, Any] = await to_thread(get_system_metrics)
            print(system_metrics)
            await sio.emit("system_info", system_metrics, room="streamstorm", callback=lambda: print("@@@"))
            await sleep(2)
            