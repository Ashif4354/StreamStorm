from logging import getLogger, Logger
from pathlib import Path
from os import listdir

from fastapi import APIRouter
from fastapi.responses import JSONResponse  # noqa: F401

from ...core.CreateChannels import CreateChannels
from ..validation import CreateChannelsData, VerifyChannelsDirectoryData
from ...settings import settings

router: APIRouter = APIRouter(prefix="/channels", tags=["Create YouTube Channels"])

logger: Logger = getLogger(f"fastapi.{__name__}")

@router.post("/create", operation_id="create_youtube_channels", summary="Create YouTube channel profiles with logos.")
def create_channels(data: CreateChannelsData) -> JSONResponse:
    """
    Create YouTube channel profiles with profile pictures.
    
    Creates channel profiles in the StreamStorm data directory
    with optional logo images (auto-generated or from provided paths).
    
    Args:
        data.channels (list): Channel configurations to create
        data.logo_needed (bool): Whether to add logos to channels
        data.random_logo (bool): Whether to use random generated logos
    
    Returns:
        success (bool): True if channels were created
        message (str): Confirmation message
        failed (list): List of channels that failed to create
    """
    # Check if user is logged in
    if not settings.is_logged_in:
        logger.error("Create channels request rejected - user not logged in")
        
        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "message": "Not logged in. Log in first.",
            }
        )
    
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
    
@router.post("/verify_dir", operation_id="verify_channels_directory", summary="Verify a directory contains valid channel logo images.")
async def verify_dir(data: VerifyChannelsDirectoryData) -> JSONResponse:
    """
    Verify a directory contains valid channel logo images.
    
    Checks that the specified directory exists, contains only valid
    image files (png, jpg, jpeg), and extracts channel names from filenames.
    
    Args:
        data.directory (str): Path to the directory to verify
    
    Returns:
        success (bool): True if directory is valid
        message (str): Result message
        files (list): List of valid channel files with names and URIs
        count (int): Number of valid channel files found
    """
    
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