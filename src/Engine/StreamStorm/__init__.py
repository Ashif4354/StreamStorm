from pathlib import Path
from sys import path

path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

from os import environ

environ.update({"BUSY": "0"})
environ.update({"BUSY_REASON": ""})

environ.update({"LIBGL_ALWAYS_SOFTWARE": "1"})
environ.update({"QT_OPENGL": "software"})
environ.update(
    {
        "QTWEBENGINE_CHROMIUM_FLAGS": "--disable-gpu --disable-gpu-compositing --disable-software-rasterizer --disable-accelerated-2d-canvas --disable-accelerated-video-decode"
    }
)


__all__: list[str] = []
