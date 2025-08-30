from os import environ
from logging import getLogger, Logger
from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse

from ..validation import ProfileData
from ...core.Profiles import Profiles

logger: Logger = getLogger("fastapi." + __name__)

router: APIRouter = APIRouter(prefix="/profiles")


@router.post("/create_profiles")
async def create_profiles(data: ProfileData) -> dict:
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
    
@router.post("/delete_all_profiles")
async def delete_all_profiles() -> dict:
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
