from logging import Logger, getLogger
from typing import Literal

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ...utils.SavedSettings import read_settings, write_settings, SavedSettings
from ..validation import AIProviderKeyData, SetDefaultProviderData
from ...settings import settings

logger: Logger = getLogger(f"fastapi.{__name__}")

router: APIRouter = APIRouter(prefix="/settings")


@router.get("/ai/keys")
async def get_ai_keys() -> JSONResponse:
    """Get all AI provider keys and default provider"""
    logger.debug("Fetching AI provider keys")

    try:
        settings: SavedSettings = await read_settings(model_format=True)

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


@router.post("/ai/keys/{provider_id}")
async def save_ai_key(
    provider_id: Literal["openai", "anthropic", "google"], data: AIProviderKeyData
) -> JSONResponse:

    logger.info(f"Saving AI key for provider: {provider_id}")

    try:
        settings: dict = await read_settings()

        # Update provider data
        settings["ai"]["providers"][provider_id]["apiKey"] = data.api_key
        settings["ai"]["providers"][provider_id]["model"] = data.model

        if data.base_url is not None:
            settings["ai"]["providers"][provider_id]["baseUrl"] = data.base_url
        elif provider_id == "openai":
            settings["ai"]["providers"][provider_id]["baseUrl"] = (
                "https://api.openai.com/v1"
            )

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
                "defaultModelUpdated": settings["ai"].get("defaultProvider")
                == provider_id,
            },
        )

    except Exception as e:
        logger.error(f"Error saving AI key for {provider_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Error saving settings: {str(e)}"},
        )


@router.post("/ai/default")
async def set_default_provider(data: SetDefaultProviderData) -> JSONResponse:
    
    logger.info(
        f"Setting default AI provider to: {data.provider} with model: {data.model}"
    )

    try:
        settings = await read_settings()

        # Set default provider, apiKey, model, and baseUrl from request data
        settings["ai"]["defaultProvider"] = data.provider
        settings["ai"]["defaultApiKey"] = data.api_key
        settings["ai"]["defaultModel"] = data.model
        settings["ai"]["defaultBaseUrl"] = data.base_url

        await write_settings(settings)

        logger.info(
            f"Default AI provider set to: {data.provider} with model: {data.model}"
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"{data.provider.capitalize()} set as default provider",
                "defaultProvider": data.provider,
                "defaultModel": data.model,
                "defaultBaseUrl": data.base_url,
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


@router.get("/ai/default")
async def get_default_provider() -> JSONResponse:
    """Get the current default AI provider with model and baseUrl"""
    logger.debug("Fetching default AI provider")

    try:
        settings = await read_settings()
        ai_settings = settings.get("ai", {})

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "defaultProvider": ai_settings.get("defaultProvider", None),
                "defaultModel": ai_settings.get("defaultModel", None),
                "defaultBaseUrl": ai_settings.get("defaultBaseUrl", None),
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
