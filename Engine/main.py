# StreamStorm - Personal Use Only
# Copyright (c) 2025 Ashif (DarkGlance)
# Licensed under the StreamStorm Personal Use License
# See LICENSE file or visit: https://github.com/Ashif4354/StreamStorm
# Unauthorized Redistribution or Commercial Use is Prohibited

from os import kill, getpid, environ
from signal import SIGTERM
from os.path import dirname, abspath, join
from threading import Thread
from logging import Logger, getLogger

from dgupdater import check_update
from uvicorn import run as run_uvicorn
from webview import create_window, start

from StreamStorm import app
from StreamStorm.utils.CustomLogger import CustomLogger
from config.config import CONFIG

CustomLogger().setup_streamstorm_logging()

logger: Logger = getLogger("streamstorm." + __name__)

def serve_api() -> None:
    logger.debug("Starting API Server")
    run_uvicorn(
        app, 
        host="0.0.0.0", 
        port=1919, # 1919, because 19 is the character number for "S" in the English alphabets.
        log_level="warning"
    ) 

def set_rammap_path() -> None:
    environ.update({"rammap_path": join(dirname(abspath(__file__)), "RAMMap.exe")})
    logger.info(f"RAMMap path set to: {environ['rammap_path']}")

def main() -> None:
    
    check_update()   

    set_rammap_path()

    Thread(target=serve_api, daemon=True).start()
    logger.info("API server started.")

    try:

        ui_url: str = "https://streamstorm-ui.web.app/" if CONFIG["ENV"] == "production" else "http://localhost:5173"
        # ui_url = "https://streamstorm-ui.web.app/"

        create_window(
            title="StreamStorm",
            url=ui_url,
            width=1300,
            height=900,
            confirm_close=True,
        )
        logger.info("Webview created.")
        start()
    finally:
        # Ensure the API is stopped when the webview is closed
        logger.info("Webview closed, stopping API server.")
        kill(getpid(), SIGTERM)
        
        
if __name__ == "__main__":
    main()
    
