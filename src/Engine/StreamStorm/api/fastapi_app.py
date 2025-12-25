from logging import DEBUG, Logger, getLogger
from typing import Callable, Optional

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from logfire import instrument_fastapi, instrument_pydantic_ai
from psutil import virtual_memory
from selenium.common.exceptions import SessionNotCreatedException

from ..settings import settings
from ..core.StreamStorm import StreamStorm
from ..utils.CustomLogger import CustomLogger
from .lib.exception_handlers import (
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

CustomLogger().setup_fastapi_logging()

logger: Logger = getLogger(f"fastapi.{__name__}")
logger.setLevel(DEBUG)

if settings.env == "development":
    logger.debug("Instrumenting atatus")

    from atatus import Client, get_client, set_response_body
    from atatus.contrib.starlette import Atatus, create_client

    atatus_client: Optional[Client] = get_client()

    if atatus_client is None:
        atatus_client = create_client(
            {
                "APP_NAME": settings.atatus_app_name,
                "LICENSE_KEY": settings.atatus_license_key,
                "APP_VERSION": settings.version,
                "TRACING": True,
                "ANALYTICS": True,
                "ANALYTICS_CAPTURE_OUTGOING": True,
                "LOG_BODY": "all",
                "LOG_LEVEL": "debug",
                "LOG_FILE": "streamstorm.log",
                "LLMOBS": True,
            }
        )

    logger.debug("Atatus client created")

else:
    logger.debug("Skipping atatus instrumentation in production")

app: FastAPI = FastAPI(lifespan=lifespan)

if settings.env == "development":
    instrument_fastapi(app)
    instrument_pydantic_ai()

app.exception_handlers = {
    Exception: common_exception_handler,
    HTTPException: common_exception_handler,
    SystemError: common_exception_handler,
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


if settings.env == "development":

    @app.middleware("http")
    async def add_atatus_set_response_body_middleware(
        request: Request, call_next: Callable
    ):
        response: Response = await call_next(request)

        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        if response_body:
            try:
                decoded_body = response_body.decode("utf-8")
                set_response_body(decoded_body)
            except Exception as e:
                logger.error(f"Error setting response body: {e}")

            headers = dict(response.headers)
            headers.pop("content-length", None)

            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=headers,
                media_type=response.media_type,
            )

        return response

    logger.debug("Atatus set_response_body middleware added to FastAPI app")

    app.add_middleware(Atatus, client=atatus_client)
    logger.debug("Atatus middleware added to FastAPI app")

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


@app.get("/config", operation_id="streamstorm_engine_config", summary="Get StreamStorm engine config and version.")
async def status() -> JSONResponse:
    """
    Get StreamStorm engine config like engine version and log file path

    Returns:
        success (bool): True if the request was successful
        version (str): StreamStorm engine version
        log_file_path (str): Path to the StreamStorm engine log file for current session
    """
    response: dict = {
        "success": True,
        "version": settings.version,
        "log_file_path": settings.log_file_path,
    }

    return JSONResponse(status_code=200, content=response)


__all__: list[str] = ["app"]
