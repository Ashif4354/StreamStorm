from logging import DEBUG, Logger, getLogger
from typing import Callable

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from psutil import virtual_memory
from selenium.common.exceptions import SessionNotCreatedException

from ..utils.CustomLogger import custom_logger
from ..utils.sentry import init_sentry
from .lib.exception_handlers import (
    business_exception_handler,
    common_exception_handler,
    session_not_created_exception_handler,
    validation_exception_handler,
)
from .lib.LifeSpan import lifespan
from .lib.middlewares import LogRequestMiddleware, RequestValidationMiddleware
from .routers.AIRouter import router as ai_router
from .routers.EnvironmentRouter import router as environment_router
from .routers.SettingsRouter import router as settings_router
from .routers.StormRouter import router as storm_router

custom_logger.setup_fastapi_logging()

logger: Logger = getLogger(f"fastapi.{__name__}")
logger.setLevel(DEBUG)

init_sentry()  # No-op if already initialised, in tests, or when no DSN is configured

app: FastAPI = FastAPI(lifespan=lifespan)



app.exception_handlers = {
    Exception: common_exception_handler,
    HTTPException: common_exception_handler,
    SystemError: business_exception_handler,
    RuntimeError: common_exception_handler,
    RequestValidationError: validation_exception_handler,
    SessionNotCreatedException: session_not_created_exception_handler,
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LogRequestMiddleware)
app.add_middleware(RequestValidationMiddleware)


@app.middleware("http")
async def add_cors_headers(request: Request, call_next: Callable):
    response: Response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


app.include_router(storm_router)
app.include_router(environment_router)
app.include_router(settings_router)
app.include_router(ai_router)


@app.get("/", operation_id="health_check", summary="Check if StreamStorm engine is running.")
async def root() -> JSONResponse:
    """
    Check if StreamStorm engine is running
    """
    
    return JSONResponse(
        status_code=200,
        content={"success": True, "message": "I am the StreamStorm Engine"},
    )


@app.get("/get_ram_info", operation_id="get_system_ram_info", summary="Get system RAM information.", deprecated=True)
async def get_ram_info() -> JSONResponse:
    """
    Get system RAM information (deprecated).
    
    Returns the current free and total RAM on the system.
    This endpoint is deprecated and may be removed in future versions.
    
    Returns:
        free (float): Available RAM in gigabytes
        total (float): Total RAM in gigabytes
    """

    return JSONResponse(
        status_code=200,
        content={
            "free": virtual_memory().available / (1024**3),
            "total": virtual_memory().total / (1024**3),
        },
    )


__all__: list[str] = ["app"]
