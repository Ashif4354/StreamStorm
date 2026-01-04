from logging import Logger, getLogger
from shutil import rmtree
from typing import Literal
from os.path import exists

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ...settings.SavedSettings import AISettings
from ..validation import AIProviderKeyData, SetDefaultProviderData, GeneralSettingsData
from ...settings import settings

logger: Logger = getLogger(f"fastapi.{__name__}")

router: APIRouter = APIRouter(prefix="/settings", tags=["Settings"])


@router.post("/general", operation_id="set_general_settings", summary="Update general application settings.")
def set_general_settings(data: GeneralSettingsData) -> JSONResponse:
    """
    Update general application settings.
    
    Args:
        data.login_method (str): Login method to use - 'cookies' or 'profiles'
    
    Returns:
        success (bool): True if settings were saved successfully
        message (str): Confirmation message
        login_method (str): Updated login method
    """
    logger.info(f"Updating general settings: login_method={data.login_method}")

    try:
        settings.login_method = data.login_method

        logger.info(f"General settings updated: login_method={settings.login_method}")

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Settings saved successfully",
                "login_method": settings.login_method,
            },
        )

    except Exception as e:
        logger.error(f"Error updating general settings: {e}")

        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Error saving settings: {str(e)}"},
        )


@router.delete("/general/clear-login-data", operation_id="clear_login_data", summary="Clear all login data including cookies and profiles.")
def clear_login_data() -> JSONResponse:
    """
    Clear all login data from the Environment directory.
    
    This removes:
    - cookies.json (saved browser cookies)
    - All temp profiles
    - Base profile
    - data.json (channel data)
    
    Returns:
        success (bool): True if data was cleared successfully
        message (str): Confirmation or error message
    """
    logger.info("Clearing all login data from Environment directory")
    
    try:
        environment_dir = settings.environment_dir
        
        if not exists(environment_dir):
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "No login data found to clear",
                },
            )
        
        # Remove the entire Environment directory and its contents
        rmtree(environment_dir)
        logger.info(f"Cleared Environment directory: {environment_dir}")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "All login data cleared successfully",
            },
        )
    
    except Exception as e:
        logger.error(f"Error clearing login data: {e}")
        
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Error clearing login data: {str(e)}"},
        )



@router.get("/", operation_id="get_settings", summary="Get all application settings including engine config, AI provider, and general settings.")
def get_settings() -> JSONResponse:
    """
    Get all application settings.
    
    Returns engine configuration (version, log file path), 
    default AI provider settings under the 'ai' sub-key,
    and general settings under the 'general' sub-key.
    
    Returns:
        success (bool): True if the request was successful
        version (str): StreamStorm engine version
        log_file_path (str): Path to the StreamStorm engine log file for current session
        ai (dict): Default AI provider settings
            - defaultProvider (str): Currently selected default AI provider
            - defaultModel (str): Currently selected model for the default provider
            - defaultBaseUrl (str): Base URL for the default provider API
        general (dict): General application settings
            - login_method (str): Current login method ('cookies' or 'profiles')
    """
    logger.debug("Fetching application settings")

    try:
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "version": settings.version,
                "log_file_path": settings.log_file_path,
                "ai": {
                    "defaultProvider": settings.ai.defaultProvider,
                    "defaultModel": settings.ai.defaultModel,
                    "defaultBaseUrl": settings.ai.defaultBaseUrl,
                },
                "general": {
                    "login_method": settings.login_method,
                    "is_logged_in": settings.is_logged_in,
                },
            },
        )

    except Exception as e:
        logger.error(f"Error fetching settings: {e}")

        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Error fetching settings: {str(e)}"},
        )


@router.get("/ai/keys", operation_id="get_ai_provider_keys", summary="Get all AI provider configurations and keys.")
def get_ai_keys() -> JSONResponse:
    """
    Get all AI provider configurations and keys.
    
    Returns the complete AI settings including API keys (masked),
    models, base URLs, and default provider configuration.
    
    Returns:
        success (bool): True if the request was successful
        providers (dict): Configuration for each AI provider (openai, anthropic, google)
        defaultProvider (str): Currently selected default provider
        defaultModel (str): Currently selected default model
        defaultBaseUrl (str): Base URL for the default provider
    """
    logger.debug("Fetching AI provider keys")

    try:
        logger.info("AI provider keys fetched successfully")

        return JSONResponse(
            status_code=200, 
            content={"success": True, **settings.ai.model_dump()}
        )

    except Exception as e:
        logger.error(f"Error fetching AI keys: {e}")

        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Error fetching AI keys: {str(e)}"},
        )


@router.post("/ai/keys/{provider_id}", operation_id="save_ai_provider_key", summary="Save API key and settings for an AI provider.")
def save_ai_key(
    provider_id: Literal["openai", "anthropic", "google"], data: AIProviderKeyData
) -> JSONResponse:
    """
    Save API key and settings for a specific AI provider.
    
    Updates the configuration for the specified AI provider including
    API key, model, and optionally base URL. If the provider is the
    current default, also updates the default model.
    
    Args:
        provider_id (str): Provider to configure - 'openai', 'anthropic', or 'google'
        data.api_key (str): API key for the provider
        data.model (str): Model name to use
        data.base_url (str, optional): Custom base URL for the API
    
    Returns:
        success (bool): True if settings were saved successfully
        message (str): Confirmation message
        defaultModelUpdated (bool): Whether the default model was also updated
    """

    logger.info(f"Saving AI key for provider: {provider_id}")

    try:
        ai_settings: AISettings = settings.ai.model_copy()

        # Update provider data
        getattr(ai_settings.providers, provider_id).apiKey = data.api_key
        getattr(ai_settings.providers, provider_id).model = data.model

        if data.base_url is not None:
            getattr(ai_settings.providers, provider_id).baseUrl = data.base_url
        elif provider_id == "openai":
            ai_settings.providers.openai.baseUrl = "https://api.openai.com/v1"

        # If this provider is the current default, update defaultModel as well
        if ai_settings.defaultProvider == provider_id:
            ai_settings.defaultModel = data.model

            logger.info(f"Updated defaultModel to: {data.model}")

        settings.ai = ai_settings  # writes to settings.json

        logger.info(f"AI key saved successfully for provider: {provider_id}")

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"{provider_id.capitalize()} settings saved successfully",
                "defaultModelUpdated": settings.ai.defaultProvider == provider_id,
            },
        )

    except Exception as e:
        logger.error(f"Error saving AI key for {provider_id}: {e}")
        
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Error saving settings: {str(e)}"},
        )



@router.post("/ai/default", operation_id="set_default_ai_provider", summary="Set the default AI provider for message generation.")
def set_default_provider(data: SetDefaultProviderData) -> JSONResponse:
    """
    Set the default AI provider for message generation.
    
    Updates the default AI provider, model, and base URL used for
    generating messages and channel names via AI.
    
    Args:
        data.provider (str): Provider to set as default - 'openai', 'anthropic', or 'google'
        data.model (str): Model name to use with the provider
        data.base_url (str): Base URL for the provider API
    
    Returns:
        success (bool): True if the default was set successfully
        message (str): Confirmation message
        defaultProvider (str): Updated default provider
        defaultModel (str): Updated default model
        defaultBaseUrl (str): Updated base URL
    """
    
    logger.info(
        f"Setting default AI provider to: {data.provider} with model: {data.model}"
    )

    try:
        ai_settings: AISettings = settings.ai.model_copy()

        # Set default provider, apiKey, model, and baseUrl from request data
        ai_settings.defaultProvider = data.provider
        ai_settings.defaultModel = data.model
        ai_settings.defaultBaseUrl = data.base_url

        settings.ai = ai_settings  # writes to settings.json

        logger.info(
            f"Default AI provider set to: {data.provider} with model: {data.model}"
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"{settings.ai.defaultProvider.capitalize()} set as default provider",
                "defaultProvider": settings.ai.defaultProvider,
                "defaultModel": settings.ai.defaultModel,
                "defaultBaseUrl": settings.ai.defaultBaseUrl,
            },
        )

    except Exception as e:
        logger.error(f"Error setting default provider: {e}")

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error setting default provider: {str(e)}",
            },
        )



