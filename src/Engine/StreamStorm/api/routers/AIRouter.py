"""
AI Router - API endpoints for AI-powered generation features.

This module provides endpoints for generating messages and channel names
using the configured AI provider.
"""

from logging import getLogger, Logger
from os.path import join, exists
from json import loads

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from platformdirs import user_data_dir
from aiofiles import open as aio_open

from ..validation import GenerateMessagesRequest, GenerateChannelNamesRequest
from ...ai import AIFactory, AIConfigurationError, AIGenerationError


logger: Logger = getLogger(f"fastapi.{__name__}")

router: APIRouter = APIRouter(prefix="/ai", tags=["AI"])

# Constants for settings
APP_DATA_DIR: str = user_data_dir("StreamStorm", "DarkGlance")
SETTINGS_FILE_PATH: str = join(APP_DATA_DIR, "settings.json")


async def get_ai_settings() -> dict | None:
    """
    Read AI settings from the settings file.
    
    Returns:
        AI settings dictionary or None if not configured
    """
    if not exists(SETTINGS_FILE_PATH):
        return None
    
    try:
        async with aio_open(SETTINGS_FILE_PATH, "r", encoding="utf-8") as file:
            content = await file.read()
            settings = loads(content)
            return settings.get("ai", None)
    except Exception as e:
        logger.error(f"Error reading AI settings: {e}")
        return None


def validate_ai_configuration(ai_settings: dict | None) -> tuple[bool, str, dict | None]:
    """
    Validate that AI is properly configured.
    
    Returns:
        Tuple of (is_valid, error_message, config_dict)
    """
    if not ai_settings:
        return False, "AI settings not found. Please configure AI in Settings.", None
    
    default_provider = ai_settings.get("defaultProvider")
    if not default_provider:
        return False, "No default AI provider configured. Please set a default provider in Settings.", None
    
    default_model = ai_settings.get("defaultModel")
    if not default_model:
        return False, "No default model configured. Please set a model in Settings.", None
    
    providers = ai_settings.get("providers", {})
    provider_config = providers.get(default_provider, {})
    
    api_key = provider_config.get("apiKey")
    if not api_key:
        return False, f"No API key configured for {default_provider}. Please add your API key in Settings.", None
    
    # Build configuration
    config = {
        "provider": default_provider,
        "model": default_model,
        "api_key": api_key,
        "base_url": ai_settings.get("defaultBaseUrl") or provider_config.get("baseUrl")
    }
    
    return True, "", config


@router.post("/generate/messages")
async def generate_messages(data: GenerateMessagesRequest) -> JSONResponse:
    """
    Generate chat messages using AI.
    
    Request body:
        - prompt: Description or context for message generation
        - count: Optional number of messages to generate (default: 10)
    
    Returns:
        - success: Boolean indicating success
        - messages: List of generated messages
        - message: Error message if failed
    """
    logger.info(f"Generating messages with prompt: {data.prompt[:50]}...")
    
    # Get and validate AI configuration
    ai_settings = await get_ai_settings()
    is_valid, error_message, config = validate_ai_configuration(ai_settings)
    
    if not is_valid:
        logger.warning(f"AI not configured: {error_message}")
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": error_message,
                "messages": []
            }
        )
    
    try:
        # Create AI service
        ai_service = AIFactory.create(
            framework="pydantic",  # Use PydanticAI as default
            provider=config["provider"],
            model=config["model"],
            api_key=config["api_key"],
            base_url=config["base_url"]
        )
        
        # Generate messages
        count = getattr(data, "count", 10) or 10
        messages = await ai_service.generate_messages(
            prompt=data.prompt,
            count=count
        )
        
        logger.info(f"Successfully generated {len(messages)} messages")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "messages": messages
            }
        )
        
    except AIConfigurationError as e:
        logger.error(f"AI configuration error: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": str(e),
                "messages": []
            }
        )
        
    except AIGenerationError as e:
        logger.error(f"AI generation error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Failed to generate messages: {str(e)}",
                "messages": []
            }
        )
        
    except Exception as e:
        logger.error(f"Unexpected error during message generation: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"An unexpected error occurred: {str(e)}",
                "messages": []
            }
        )


@router.post("/generate/channel-names")
async def generate_channel_names(data: GenerateChannelNamesRequest) -> JSONResponse:
    """
    Generate YouTube channel name suggestions using AI.
    
    Request body:
        - topic: Topic or theme for channel names
        - count: Optional number of names to generate (default: 5)
    
    Returns:
        - success: Boolean indicating success
        - channelNames: List of suggested channel names
        - message: Error message if failed
    """
    logger.info(f"Generating channel names for topic: {data.topic[:50]}...")
    
    # Get and validate AI configuration
    ai_settings = await get_ai_settings()
    is_valid, error_message, config = validate_ai_configuration(ai_settings)
    
    if not is_valid:
        logger.warning(f"AI not configured: {error_message}")
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": error_message,
                "channelNames": []
            }
        )
    
    try:
        # Create AI service
        ai_service = AIFactory.create(
            framework="pydantic",
            provider=config["provider"],
            model=config["model"],
            api_key=config["api_key"],
            base_url=config["base_url"]
        )
        
        # Generate channel names
        count = getattr(data, "count", 5) or 5
        channel_names = await ai_service.generate_channel_names(
            topic=data.topic,
            count=count
        )
        
        logger.info(f"Successfully generated {len(channel_names)} channel names")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "channelNames": channel_names
            }
        )
        
    except AIConfigurationError as e:
        logger.error(f"AI configuration error: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": str(e),
                "channelNames": []
            }
        )
        
    except AIGenerationError as e:
        logger.error(f"AI generation error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Failed to generate channel names: {str(e)}",
                "channelNames": []
            }
        )
        
    except Exception as e:
        logger.error(f"Unexpected error during channel name generation: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"An unexpected error occurred: {str(e)}",
                "channelNames": []
            }
        )


@router.get("/status")
async def get_ai_status() -> JSONResponse:
    """
    Get the current AI configuration status.
    
    Returns:
        - configured: Boolean indicating if AI is properly configured
        - provider: Current default provider (if configured)
        - model: Current default model (if configured)
    """
    ai_settings = await get_ai_settings()
    is_valid, error_message, config = validate_ai_configuration(ai_settings)
    
    if is_valid:
        return JSONResponse(
            status_code=200,
            content={
                "configured": True,
                "provider": config["provider"],
                "model": config["model"],
                "hasBaseUrl": config["base_url"] is not None
            }
        )
    else:
        return JSONResponse(
            status_code=200,
            content={
                "configured": False,
                "message": error_message
            }
        )


@router.get("/providers")
async def get_supported_providers() -> JSONResponse:
    """
    Get list of supported AI providers and their default models.
    
    Returns:
        List of provider information with default models
    """
    providers = [
        {
            "id": "openai",
            "name": "OpenAI",
            "defaultModel": "gpt-4o-mini",
            "suggestedModels": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
        },
        {
            "id": "anthropic",
            "name": "Anthropic",
            "defaultModel": "claude-3-5-sonnet-20241022",
            "suggestedModels": ["claude-3-opus-20240229", "claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]
        },
        {
            "id": "google",
            "name": "Google",
            "defaultModel": "gemini-1.5-flash",
            "suggestedModels": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"]
        }
    ]
    
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "providers": providers
        }
    )


__all__: list[str] = ["router"]
