from logging import Logger, getLogger

from fastapi import APIRouter
from fastapi.responses import JSONResponse

# from ...ai.Langchain import LangchainAI
from ...ai.PydanticAI import PydanticAI
from ..validation import GenerateMessagesRequest
from .SettingsRouter import read_settings
from ...utils.SavedSettings import SavedSettings

logger: Logger = getLogger(f"fastapi.{__name__}")

router: APIRouter = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/generate/messages")
async def generate_messages(data: GenerateMessagesRequest) -> JSONResponse:
    logger.info(f"Generating messages with prompt: {data.prompt[:50]}...")
    settings: SavedSettings = await read_settings(model_format=True)
    provider_name = settings.ai.defaultProvider

    AI = PydanticAI(
        provider_name=provider_name,
        model_name=settings.ai.defaultModel,
        api_key=getattr(settings.ai.providers, provider_name).apiKey,
        base_url=settings.ai.defaultBaseUrl,
    )

    logger.info(f"Using provider: {provider_name}, model: {settings.ai.defaultModel}")

    messages = await AI.generate_messages(data.prompt)

    return JSONResponse(
        status_code=200, content={"success": True, "messages": messages}
    )


@router.post("/generate/channel-names")
async def generate_channel_names(data: GenerateMessagesRequest) -> JSONResponse:
    logger.info(f"Generating channel names with prompt: {data.prompt[:50]}...")
    settings: SavedSettings = await read_settings(model_format=True)
    provider_name = settings.ai.defaultProvider

    AI = PydanticAI(
        provider_name=provider_name,
        model_name=settings.ai.defaultModel,
        api_key=getattr(settings.ai.providers, provider_name).apiKey,
        base_url=settings.ai.defaultBaseUrl,
    )

    logger.info(f"Using provider: {provider_name}, model: {settings.ai.defaultModel}")
    
    channel_names = await AI.generate_channels(data.prompt)

    return JSONResponse(
        status_code=200, content={"success": True, "channelNames": channel_names}
    )


__all__: list[str] = ["router"]
