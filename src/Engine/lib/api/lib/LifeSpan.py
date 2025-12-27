from typing import Any, AsyncGenerator
from fastapi import FastAPI
from contextlib import asynccontextmanager
from asyncio import create_task, get_running_loop
from logging import Logger, getLogger

from ...utils.StormStopper import background_storm_stopper
from ...utils.SystemInfoEmitter import emit_system_metrics
from ...utils.CustomLogger import set_logging_loop
logger: Logger = getLogger(f"fastapi.{__name__}")

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    logger.info("Starting StreamStorm Engine...")
    
    # Set the logging loop for CustomLogger
    set_logging_loop(get_running_loop())
    
    # Start the background storm stopper task
    create_task(background_storm_stopper())
    
    # Start the system info emitter task
    create_task(emit_system_metrics())
    

    yield

    logger.info("Shutting Down Engine....")


__all__: list[str] = ["lifespan"]