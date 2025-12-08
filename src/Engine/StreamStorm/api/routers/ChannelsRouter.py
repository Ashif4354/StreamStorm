from logging import getLogger, Logger
from pathlib import Path
from os import listdir

from fastapi import APIRouter
from fastapi.responses import JSONResponse  # noqa: F401

from .ProfileRouter import router as profile_router
from ...core.CreateChannels import CreateChannels
from ..validation import CreateChannelsData, VerifyChannelsDirectoryData

router: APIRouter = APIRouter(prefix="/channels")

router.include_router(profile_router)

logger: Logger = getLogger(f"fastapi.{__name__}")

@router.post("/create")
def create_channels(data: CreateChannelsData) -> JSONResponse:
    
    cc: CreateChannels = CreateChannels(data.logo_needed, data.random_logo)
    failed_list : list = cc.start(data.channels)
    
    response: dict = {
        "success": True,
        "message": "Channels created successfully",
        "failed": failed_list
    }
    
    logger.info("Channels created successfully")
    
    return JSONResponse(
        status_code=200,
        content=response
    )
    
@router.post("/verify_dir")
async def verify_dir(data: VerifyChannelsDirectoryData) -> JSONResponse:
    
    path: Path = Path(data.directory)

    if not path.exists():
        logger.error("Directory not found")
        
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": "Directory not found"
            }
        )

    if not path.is_dir():
        logger.error("Provided path is not a directory")
        
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Provided path is not a directory"
            }
        )

    files: list = listdir(path)

    if not files:
        logger.error("Directory is empty")
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Directory is empty"
            }
        )

    new_files: list = []

    for file in files:
        
        if (path / file).is_dir():
            logger.error("Directory contains folders (Only files are supported)")
            
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "Directory contains folders (Only files are supported)"
                }
            )
                
        if not file.endswith(".png") and not file.endswith(".jpg") and not file.endswith(".jpeg"):
            logger.error("Directory contains non-image files (Only png, jpg and jpeg files are supported)")
            
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "Directory contains non-image files (Only png, jpg and jpeg files are supported)"
                }
            ) 

        channel_name: str = '.'.join(file.split(".")[:-1])
        
        new_files.append({
            "name": channel_name,
            "uri": str(path / file)
        })

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Directory verified successfully",
            "files": new_files,
            "count": len(new_files),
        }
    )