from os import environ
from logging import getLogger, Logger
from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse

from ..validation import ProfileData
from ...core.Profiles import Profiles

logger: Logger = getLogger(f"fastapi.{__name__}")

router: APIRouter = APIRouter(prefix="/profiles", tags=["Manage Profiles"])

@router.post("/create", operation_id="create_chromium_profiles", summary="Create Chromium browser profiles for storming.")
async def create_profiles(data: ProfileData) -> dict:
    """
    Create temporary Chromium browser profiles for storming.
    
    Creates the specified number of Chromium browser profiles
    in the StreamStorm data directory for use during storms.
    Sets the environment to BUSY during creation.
    
    Args:
        data.count (int): Number of profiles to create
    
    Returns:
        success (bool): True if profiles were created successfully
        message (str): Confirmation message
    """
    environ.update({"BUSY": "1", "BUSY_REASON": "Creating profiles"})

    profiles: Profiles = Profiles()
    
    try:
        await run_in_threadpool(profiles.create_profiles, data.count)
        logger.info(f"Created {data.count} profiles")
    finally:
        environ.update({"BUSY": "0", "BUSY_REASON": ""})
    
    return JSONResponse(
        status_code=200, 
        content={
            "success": True, 
            "message": "Profiles created successfully"
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
    environ.update({"BUSY": "1", "BUSY_REASON": "Deleting profiles"})

    profiles: Profiles = Profiles()

    try:
        await run_in_threadpool(profiles.delete_all_temp_profiles)
    finally:
        environ.update({"BUSY": "0", "BUSY_REASON": ""})

    return JSONResponse(
        status_code=200, 
        content={
            "success": True, 
            "message": "Profiles deleted successfully"
        }
    )
