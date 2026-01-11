from logging import getLogger, Logger
from json import loads as json_loads, JSONDecodeError
from typing import Any

from fastapi import APIRouter, UploadFile, File
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse

from ..validation import ProfileData
from ...core.Profiles import Profiles
from ...core.EngineContext import EngineContext
from ...utils.cookies import parse_netscape_cookies

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

    busy_message: str = "Logging in" if data.cookies_login else "Creating profiles"
    
    EngineContext.set_busy(busy_message)
    profiles: Profiles = Profiles()
    
    try:
        await run_in_threadpool(profiles.create_profiles, data.count)

        if data.cookies_login:
            logger.info("Cookie login completed")
        else:
            logger.info(f"Created {data.count} profiles")

    except Exception as e:
        logger.error(f"Error occurred while creating profiles: {e}")
        raise SystemError("An error occurred while creating profiles") from e
        
    finally:
        EngineContext.reset()
    
    success_message = "Login successful, cookies saved" if data.cookies_login else "Profiles created successfully"
    
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

@router.post("/save_cookies", operation_id="save_cookie_files", summary="Upload and save cookie files (JSON or Netscape format).")
async def save_cookies(files: list[UploadFile] = File(...)) -> JSONResponse:
    """
    Upload and parse cookie files to set up authentication.
    
    Accepts multiple cookie files in either JSON or Netscape format.
    Combines all cookies and creates the base profile with them.
    
    Supported formats:
    - JSON: Standard browser cookie export format (array of cookie objects)
    - Netscape: Tab or space-separated format used by curl and browser extensions
    
    Args:
        files: List of cookie files to upload
    
    Returns:
        success (bool): True if cookies were saved successfully
        message (str): Confirmation message
    """
    if not files:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "No files provided"
            }
        )
    
    all_cookies: list[dict[str, Any]] = []
    invalid_files: list[str] = []
    
    for file in files:
        try:
            content = await file.read()
            content_str = content.decode('utf-8')
            
            # Try parsing as JSON first
            try:
                parsed = json_loads(content_str)
                if isinstance(parsed, list):
                    # Validate that each item looks like a cookie
                    for cookie in parsed:
                        if isinstance(cookie, dict) and 'name' in cookie and 'value' in cookie:
                            all_cookies.append(cookie)
                        else:
                            raise ValueError("Invalid cookie object structure")
                else:
                    raise ValueError("JSON must be an array of cookies")
                    
                logger.info(f"Parsed {file.filename} as JSON format")
                
            except (JSONDecodeError, ValueError):
                # Try parsing as Netscape format
                try:
                    parsed_cookies = parse_netscape_cookies(content_str, file.filename)
                    all_cookies.extend(parsed_cookies)
                    logger.info(f"Parsed {file.filename} as Netscape format")
                    
                except Exception as e:
                    logger.error(f"Failed to parse {file.filename}: {e}")
                    invalid_files.append(file.filename)
                    
        except Exception as e:
            logger.error(f"Error reading file {file.filename}: {e}")
            invalid_files.append(file.filename)
    
    if invalid_files:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": f"Invalid cookie file format: {', '.join(invalid_files)}"
            }
        )
    
    if not all_cookies:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "No valid cookies found in uploaded files"
            }
        )

    # with open("cookies.json", "w") as f:
    #     from json import dump as json_dump
    #     json_dump(all_cookies, f, indent=4)

    EngineContext.set_busy("Saving cookies and creating profile")
    profiles: Profiles = Profiles()
    
    try:
        await run_in_threadpool(profiles.create_profiles, None, all_cookies)
        logger.info(f"Saved {len(all_cookies)} cookies from uploaded files")
        
    except Exception as e:
        logger.error(f"Error creating profile with cookies: {e} || {str(e)}")
        EngineContext.reset()
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Failed to save cookies: {str(e)}"
            }
        )
    finally:
        EngineContext.reset()
    
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": f"Successfully saved {len(all_cookies)} cookies from {len(files)} file(s)"
        }
    )
