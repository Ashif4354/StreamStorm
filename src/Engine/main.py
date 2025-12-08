# StreamStorm - Personal Use Only
# Copyright (c) 2025 Ashif (DarkGlance)
# Licensed under the StreamStorm Personal Use License
# See LICENSE file or visit: https://github.com/Ashif4354/StreamStorm
# Unauthorized Redistribution or Commercial Use is Prohibited

from os import kill, getpid
from signal import SIGTERM
from threading import Thread
from logging import Logger, getLogger

from dgupdater import check_update
from uvicorn import run as run_uvicorn
from webview import create_window, start
from socketio import ASGIApp

from StreamStorm.api.fastapi_app import app as fastapi_app
from StreamStorm.utils.CustomLogger import CustomLogger
from StreamStorm.config.config import CONFIG
from StreamStorm.socketio.sio import sio

CustomLogger().setup_streamstorm_logging()

logger: Logger = getLogger(f"streamstorm.{__name__}") 

def serve_api() -> None:
    logger.debug("Starting API-SocketIO Server") 
    
    app: ASGIApp = ASGIApp(sio, fastapi_app)
    
    run_uvicorn(
        app, 
        host="0.0.0.0", 
        port=1919, # 1919, because 19 is the character number for "S" in the English alphabets.
        log_level="warning"
    ) 

def main() -> None:
    
    if CONFIG["OS"] == "Windows":
        check_update(parallel=True)

    Thread(target=serve_api, daemon=True).start()
    logger.info("API server started.")
    
    # Comment this below two line after testing
    # if CONFIG["ENV"] == "development":
    #     input()
    #     return

    try:

        ui_url: str = "https://streamstorm-ui.darkglance.in/" if CONFIG["ENV"] == "production" else "http://localhost:5173"
        # ui_url = "https://streamstorm-ui.darkglance.in/" 
        
        logger.debug(f"UI URL: {ui_url}")

        create_window(
            title="StreamStorm",
            url=ui_url,
            width=1300,
            height=900,
            confirm_close=True,
        )
        logger.info("Webview created.")
        
        if CONFIG["OS"] == "Linux":
            start(gui='qt')
        else:
            start()
            
        logger.info("Webview started.")
    finally:
        # Ensure the API is stopped when the webview is closed
        logger.info("Webview closed, stopping API server.")
        kill(getpid(), SIGTERM)
        
        
if __name__ == "__main__":
    main()
    
