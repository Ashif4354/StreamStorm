from typing import Callable, Optional
from logging import DEBUG, getLogger, Logger
from psutil import virtual_memory
from os import environ

from ..config import CONFIG

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from selenium.common.exceptions import SessionNotCreatedException

from ..core.StreamStorm import StreamStorm
from .lib.exception_handlers import (
    common_exception_handler,
    validation_exception_handler,
    session_not_created_exception_handler
)
from .lib.LifeSpan import lifespan
from .lib.middlewares import LogRequestMiddleware, RequestValidationMiddleware
from ..utils.CustomLogger import CustomLogger
from .routers.StormRouter import router as storm_router
from .routers.EnvironmentRouter import router as environment_router


CustomLogger().setup_fastapi_logging()

logger: Logger = getLogger(f"fastapi.{__name__}")
logger.setLevel(DEBUG)

if CONFIG["ENV"] == "development":
    logger.debug("Instrumenting atatus")

    from dotenv import load_dotenv
    load_dotenv()

    from atatus import Client, get_client, set_response_body
    from atatus.contrib.starlette import create_client, Atatus

    atatus_client: Optional[Client] = get_client()

    if atatus_client is None:
        atatus_client = create_client(
            {
                'APP_NAME': environ.get('ATATUS_APP_NAME'),
                'LICENSE_KEY': environ.get('ATATUS_LICENSE_KEY'),
                'APP_VERSION': CONFIG["VERSION"],
                'TRACING': True,
                'ANALYTICS': True,
                'ANALYTICS_CAPTURE_OUTGOING': True,
                'LOG_BODY': 'all',
                'LOG_LEVEL': 'debug',
                'LOG_FILE': 'streamstorm.log'
            }
        )

    logger.debug("Atatus client created")

else:
    logger.debug("Skipping atatus instrumentation in production")

app: FastAPI = FastAPI(lifespan=lifespan)

app.exception_handlers = {
    Exception: common_exception_handler,
    HTTPException: common_exception_handler,
    SystemError: common_exception_handler,
    RuntimeError: common_exception_handler,
    RequestValidationError: validation_exception_handler,
    SessionNotCreatedException: session_not_created_exception_handler
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

if CONFIG["ENV"] == "development":
    
    # @app.middleware("http")
    # async def add_atatus_set_response_body_middleware(request: Request, call_next: Callable):
    #     response: Response = await call_next(request)
        
    #     if request.method == "POST":
    #         set_response_body(response.body)
            
    #     return response
    
    # logger.debug("Atatus set_response_body middleware added to FastAPI app")    
    
    app.add_middleware(Atatus, client=atatus_client)
    logger.debug("Atatus middleware added to FastAPI app")

app.include_router(storm_router)
app.include_router(environment_router)

@app.get("/")
async def root() -> JSONResponse:
    
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "I am the StreamStorm Engine"
        }
    )

    
@app.get("/get_ram_info")
async def get_ram_info() -> JSONResponse:
    return JSONResponse(
        status_code=200, 
        content={
            "free": virtual_memory().available / (1024**3), 
            "total": virtual_memory().total / (1024**3)
        }
    )
    
@app.get("/engine-status")
async def status() -> JSONResponse:
    response: dict = {
        "storm_in_progress": False,
        "version": CONFIG["VERSION"]
    }

    if StreamStorm.ss_instance is not None:
        response["storm_in_progress"] = True

    return JSONResponse(
        status_code=200, 
        content=response
    )
    

__all__: list[str] = ["app"]
