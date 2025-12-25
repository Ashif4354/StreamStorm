from logging import Logger, getLogger
from typing import Literal

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ...settings.SavedSettings import AISettings
from ..validation import AIProviderKeyData, SetDefaultProviderData
from ...settings import settings

logger: Logger = getLogger(f"fastapi.{__name__}")

router: APIRouter = APIRouter(prefix="/settings", tags=["Settings"])


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


@router.get("/ai/default", operation_id="get_default_ai_provider", summary="Get the current default AI provider configuration.")
def get_default_provider() -> JSONResponse:
    """
    Get the current default AI provider configuration.
    
    Returns the currently selected default AI provider along with
    its model and base URL settings.
    
    Returns:
        success (bool): True if the request was successful
        defaultProvider (str): Currently selected default provider
        defaultModel (str): Currently selected model for the default provider
        defaultBaseUrl (str): Base URL for the default provider API
    """
    logger.debug("Fetching default AI provider")

    try:
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "defaultProvider": settings.ai.defaultProvider,
                "defaultModel": settings.ai.defaultModel,
                "defaultBaseUrl": settings.ai.defaultBaseUrl,
            },
        )

    except Exception as e:
        logger.error(f"Error fetching default provider: {e}")

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error fetching default provider: {str(e)}",
            },
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



