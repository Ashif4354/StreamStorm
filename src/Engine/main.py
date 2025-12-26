# StreamStorm - Personal Use Only
# Copyright (c) 2025 Ashif (DarkGlance)
# Licensed under the StreamStorm Personal Use License
# See LICENSE file or visit: https://github.com/Ashif4354/StreamStorm
# Unauthorized Redistribution or Commercial Use is Prohibited

from contextlib import suppress

with suppress(ImportError):
    from dotenv import load_dotenv

    load_dotenv()

from logging import Logger, getLogger
from os import getpid, kill
from signal import SIGTERM
from threading import Thread

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dgupdater import check_update
from logfire import configure as logfire_configure
from socketio import ASGIApp
from uvicorn import run as run_uvicorn
from webview import create_window, start

from StreamStorm.settings import settings
from StreamStorm.utils.CombinedLifeSpan import combined_lifespan

logfire_configure(
    token=settings.logfire_token, 
    service_name="StreamStorm", 
    environment=settings.env, 
    console=False
)

from StreamStorm.api.fastapi_app import app as fastapi_app
from StreamStorm.socketio.sio import sio
from StreamStorm.mcp.mcpserver import mcp_app
from StreamStorm.utils.CustomLogger import custom_logger

custom_logger.setup_streamstorm_logging()

logger: Logger = getLogger(f"streamstorm.{__name__}")


def exit_app() -> None:
    logger.debug("Exiting StreamStorm")
    kill(getpid(), SIGTERM)


def serve_api() -> None:
    logger.debug("Starting API-SocketIO Server")
    
    new_app: FastAPI = FastAPI(
        title="StreamStorm API with MCP Server",
        version=settings.version,
        routes=[
            *mcp_app.routes
        ],
        lifespan=combined_lifespan,
        docs_url="/mcp-docs",
        openapi_url="/mcp-openapi.json"
    )

    new_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    new_app.mount("/", fastapi_app)

    app: ASGIApp = ASGIApp(sio, new_app)
    HOST: str = settings.host
    PORT: int = settings.port

    logger.info(f"StreamStorm Engine listening at {HOST}:{PORT}")

    run_uvicorn(
        app,
        host=HOST,
        port=PORT,
        log_level="warning",
    )


def main() -> None:
    if settings.run_only_api:
        serve_api()
        return

    if settings.os == "Windows":
        check_update(parallel=True)

    Thread(target=serve_api, daemon=True).start()
    logger.debug("API server started.")

    try:
        ui_url: str = (
            "https://streamstorm-ui.darkglance.in/"
            if settings.env == "production"
            else "http://localhost:5173"
        )
        # ui_url = "https://streamstorm-ui.darkglance.in/"

        logger.debug(f"UI URL: {ui_url}")

        create_window(
            title="StreamStorm",
            url=ui_url,
            width=1400,
            height=900,
            confirm_close=True,
        )
        logger.debug("Webview created.")

        if settings.os == "Linux":
            start(gui="qt")
        else:
            start()

        logger.debug("Webview started.")
    finally:
        # Ensure the API is stopped when the webview is closed
        logger.debug("Webview closed, stopping API server.")
        exit_app()


if __name__ == "__main__":
    main()
