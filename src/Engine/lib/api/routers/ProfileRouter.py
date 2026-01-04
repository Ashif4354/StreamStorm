from logging import getLogger, Logger
from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse

from ..validation import ProfileData
from ...core.Profiles import Profiles
from ...core.EngineContext import EngineContext
from ...settings import settings

logger: Logger = getLogger(f"fastapi.{__name__}")

router: APIRouter = APIRouter(prefix="/profiles", tags=["Manage Profiles"])

@router.post("/create", operation_id="create_chromium_profiles", summary="Create Chromium browser profiles or login with cookies.")
async def create_profiles(data: ProfileData) -> dict:
    """
    Create temporary Chromium browser profiles for storming or login with cookies.
    
    If login_method is 'cookies' (count is None/omitted):
        Opens a browser for Google login and saves cookies.
    
    If login_method is 'profiles' (count >= 1):
        Creates the specified number of Chromium browser profiles.
    
    Args:
        data.count (int, optional): Number of profiles to create. 
            - Required for profile-based login (must be >= 1)
            - Optional/null for cookie-based login
    
    Returns:
        success (bool): True if operation was successful
        message (str): Confirmation message
    """
    # Cookie-based login (count is None)
    is_cookie_login = data.count is None
    busy_message = "Logging in" if is_cookie_login else "Creating profiles"
    
    EngineContext.set_busy(busy_message)
    profiles: Profiles = Profiles()
    
    try:
        await run_in_threadpool(profiles.create_profiles, data.count)

        if is_cookie_login:
            logger.info("Cookie login completed")
        else:
            logger.info(f"Created {data.count} profiles")
    except Exception as e:
        logger.error(f"Error occurred while creating profiles: {e}")
        raise SystemError("An error occurred while creating profiles") from e
        
    finally:
        EngineContext.reset()
    
    success_message = "Login successful, cookies saved" if is_cookie_login else "Profiles created successfully"
    
    return JSONResponse(
        status_code=200, 
        content={
            "success": True, 
            "message": success_message
        }
    )
    
@router.post("/delete", operation_id="delete_chromium_profiles", summary="Delete all temporary Chromium browser profiles.")
async def delete_all_profiles() -> dict:
    """
    Delete all temporary Chromium browser profiles.
    
    Removes all temporary profiles created by StreamStorm.
    Sets the environment to BUSY during deletion.
    
    Returns:
        success (bool): True if profiles were deleted successfully
        message (str): Confirmation message
    """
    EngineContext.set_busy("Deleting profiles")

    profiles: Profiles = Profiles()

    try:
        await run_in_threadpool(profiles.delete_all_temp_profiles)
    finally:
        EngineContext.reset()

    return JSONResponse(
        status_code=200, 
        content={
            "success": True, 
            "message": "Profiles deleted successfully"
        }
    )
