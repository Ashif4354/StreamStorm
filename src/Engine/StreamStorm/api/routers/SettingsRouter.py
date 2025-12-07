from logging import getLogger, Logger
from os.path import join, exists
from os import makedirs
from json import JSONDecodeError, loads, dumps
from typing import Literal

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from platformdirs import user_data_dir
from aiofiles import open as aio_open

from ..validation import AIProviderKeyData, SetDefaultProviderData


logger: Logger = getLogger(f"fastapi.{__name__}")

router: APIRouter = APIRouter(prefix="/settings")

# Constants
APP_DATA_DIR: str = user_data_dir("StreamStorm", "DarkGlance")
SETTINGS_FILE_PATH: str = join(APP_DATA_DIR, "settings.json")

# Default settings structure
DEFAULT_SETTINGS: dict = {
    "ai": {
        "providers": {
            "openai": {
                "apiKey": "",
                "model": "",
                "baseUrl": "https://api.openai.com/v1"
            },
            "anthropic": {
                "apiKey": "",
                "model": ""
            },
            "google": {
                "apiKey": "",
                "model": ""
            }
        },
        "defaultProvider": None,
        "defaultModel": None
    }
}


async def ensure_settings_file() -> None:
    """Ensure the settings file and directory exist"""
    if not exists(APP_DATA_DIR):
        makedirs(APP_DATA_DIR, exist_ok=True)
        logger.info(f"Created settings directory: {APP_DATA_DIR}")
    
    if not exists(SETTINGS_FILE_PATH):
        async with aio_open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as file:
            await file.write(dumps(DEFAULT_SETTINGS, indent=2))
        logger.info(f"Created default settings file: {SETTINGS_FILE_PATH}")


async def read_settings() -> dict:
    """Read settings from file, create if not exists"""
    await ensure_settings_file()
    
    try:
        async with aio_open(SETTINGS_FILE_PATH, "r", encoding="utf-8") as file:
            content = await file.read()
            settings = loads(content)
            
            # Ensure AI section exists
            if "ai" not in settings:
                settings["ai"] = DEFAULT_SETTINGS["ai"]
                
            return settings
            
    except (JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error reading settings file, recreating: {e}")
        async with aio_open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as file:
            await file.write(dumps(DEFAULT_SETTINGS, indent=2))
        return DEFAULT_SETTINGS.copy()


async def write_settings(settings: dict) -> None:
    """Write settings to file"""
    await ensure_settings_file()
    
    async with aio_open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as file:
        await file.write(dumps(settings, indent=2))


@router.get("/ai/keys")
async def get_ai_keys() -> JSONResponse:
    """Get all AI provider keys and default provider"""
    logger.debug("Fetching AI provider keys")
    
    try:
        settings = await read_settings()
        ai_settings = settings.get("ai", DEFAULT_SETTINGS["ai"])
        providers = ai_settings.get("providers", {})
        default_provider = ai_settings.get("defaultProvider", None)
        
        # Mask API keys for security (show only last 4 chars)
        response_data = {}
        for provider_id, provider_data in providers.items():
            response_data[provider_id] = {
                "apiKey": provider_data.get("apiKey", ""),
                "model": provider_data.get("model", ""),
            }
            if "baseUrl" in provider_data:
                response_data[provider_id]["baseUrl"] = provider_data.get("baseUrl", "")
        
        response_data["defaultProvider"] = default_provider
        response_data["defaultModel"] = ai_settings.get("defaultModel", None)
        
        logger.info("AI provider keys fetched successfully")
        
        return JSONResponse(
            status_code=200,
            content=response_data
        )
        
    except Exception as e:
        logger.error(f"Error fetching AI keys: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error fetching AI keys: {str(e)}"
            }
        )


@router.post("/ai/keys/{provider_id}")
async def save_ai_key(provider_id: Literal["openai", "anthropic", "google"], data: AIProviderKeyData) -> JSONResponse:
    """Save AI provider key configuration"""
    logger.info(f"Saving AI key for provider: {provider_id}")
    
    try:
        settings = await read_settings()
        
        # Ensure structure exists
        if "ai" not in settings:
            settings["ai"] = DEFAULT_SETTINGS["ai"]
        if "providers" not in settings["ai"]:
            settings["ai"]["providers"] = DEFAULT_SETTINGS["ai"]["providers"]
        if provider_id not in settings["ai"]["providers"]:
            settings["ai"]["providers"][provider_id] = {}
        
        # Update provider data
        settings["ai"]["providers"][provider_id]["apiKey"] = data.apiKey
        settings["ai"]["providers"][provider_id]["model"] = data.model
        
        if data.baseUrl is not None:
            settings["ai"]["providers"][provider_id]["baseUrl"] = data.baseUrl
        elif provider_id == "openai":
            settings["ai"]["providers"][provider_id]["baseUrl"] = "https://api.openai.com/v1"
        
        # If this provider is the current default, update defaultModel as well
        if settings["ai"].get("defaultProvider") == provider_id:
            settings["ai"]["defaultModel"] = data.model
            logger.info(f"Updated defaultModel to: {data.model}")
        
        await write_settings(settings)
        
        logger.info(f"AI key saved successfully for provider: {provider_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"{provider_id.capitalize()} settings saved successfully",
                "defaultModelUpdated": settings["ai"].get("defaultProvider") == provider_id
            }
        )
        
    except Exception as e:
        logger.error(f"Error saving AI key for {provider_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error saving settings: {str(e)}"
            }
        )


@router.post("/ai/default")
async def set_default_provider(data: SetDefaultProviderData) -> JSONResponse:
    """Set the default AI provider"""
    logger.info(f"Setting default AI provider to: {data.provider}")
    
    try:
        settings = await read_settings()
        
        # Ensure structure exists
        if "ai" not in settings:
            settings["ai"] = DEFAULT_SETTINGS["ai"]
        
        # Check if provider has API key configured
        providers = settings["ai"].get("providers", {})
        provider_config = providers.get(data.provider, {})
        
        if not provider_config.get("apiKey"):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": f"Cannot set {data.provider} as default: API key not configured"
                }
            )
        
        if not provider_config.get("model"):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": f"Cannot set {data.provider} as default: Model not selected"
                }
            )
        
        # Set default provider and model
        settings["ai"]["defaultProvider"] = data.provider
        settings["ai"]["defaultModel"] = provider_config.get("model", "")
        
        await write_settings(settings)
        
        logger.info(f"Default AI provider set to: {data.provider} with model: {provider_config.get('model')}")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"{data.provider.capitalize()} set as default provider",
                "defaultModel": provider_config.get("model", "")
            }
        )
        
    except Exception as e:
        logger.error(f"Error setting default provider: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error setting default provider: {str(e)}"
            }
        )


@router.get("/ai/default")
async def get_default_provider() -> JSONResponse:
    """Get the current default AI provider"""
    logger.debug("Fetching default AI provider")
    
    try:
        settings = await read_settings()
        default_provider = settings.get("ai", {}).get("defaultProvider", None)
        default_model = settings.get("ai", {}).get("defaultModel", None)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "defaultProvider": default_provider,
                "defaultModel": default_model
            }
        )
        
    except Exception as e:
        logger.error(f"Error fetching default provider: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error fetching default provider: {str(e)}"
            }
        )
