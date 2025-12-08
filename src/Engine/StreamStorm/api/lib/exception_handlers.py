from logging import Logger, getLogger

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger: Logger = getLogger(f"fastapi.{__name__}")

async def common_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Common exception handler for all exceptions.
    """
    logger.error(f"An error occurred: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": f"An error occurred: {str(exc)}"},
    )
    
    
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    logger.debug(f"Validation errors: {errors}")
    
    field_map: dict[str, str] = {
        "slow_mode": "Slow mode",
        "slowMode": "Slow mode",
        "messages": "Messages",
        "video_url": "Video URL",
        "videoUrl": "Video URL",
        "chat_url": "Chat URL",
        "chatUrl": "Chat URL",
        "subscribe": "Subscribe",
        "subscribe_and_wait": "Subscribe and wait",
        "subscribeAndWait": "Subscribe and wait",
        "subscribe_and_wait_time": "Subscribe and wait time",
        "subscribeAndWaitTime": "Subscribe and wait time",
        "channels": "Channels",
        "background": "Background",
        "count": "Profiles count",
        "mode": "Channels selection mode",
        "directory": "Logos directory"
    }
    
    message: str = field_map[errors[0]["loc"][1]] + ": " + errors[0]["msg"][6:].capitalize()
    
    if "ctx" in errors[0]:
        del errors[0]["ctx"]

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": message,
            "context": errors
        }
    )
    

async def session_not_created_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    message: str = str(exc)
    
    logger.error(f"Session not created: {message}")
    
    if "this version of chromedriver only supports chrome version" in message.lower():
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Update your Chrome to the latest version first"},
        )
    else:        
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Session not created: {str(exc)}"},
        )
    
__all__: list[str] = [
    "common_exception_handler",
    "validation_exception_handler",
    "session_not_created_exception_handler"
]

