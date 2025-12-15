from logging import getLogger, Logger

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..validation import GenerateMessagesRequest
from .SettingsRouter import read_settings
from ...ai.Langchain import LangchainAI


logger: Logger = getLogger(f"fastapi.{__name__}")

router: APIRouter = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/generate/messages")
async def generate_messages(data: GenerateMessagesRequest) -> JSONResponse:
    logger.info(f"Generating messages with prompt: {data.prompt[:50]}...")
    settings: dict = await read_settings()

    model = LangchainAI(
        provider_name=settings["ai"]["defaultProvider"],
        model_name=settings["ai"]["defaultModel"],
        api_key=settings["ai"]["providers"][provider_name]["apiKey"],
        base_url=settings["ai"]["defaultBaseUrl"]
    )

    messages = model.generate_messages(data.prompt)

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "messages": messages
        }
    )


@router.post("/generate/channel-names")
async def generate_channel_names(data: GenerateMessagesRequest) -> JSONResponse:
    logger.info(f"Generating channel names with prompt: {data.prompt[:50]}...")
    settings: dict = await read_settings()

    model = LangchainAI(
        provider_name=settings["ai"]["defaultProvider"],
        model_name=settings["ai"]["defaultModel"],
        api_key=settings["ai"]["providers"][provider_name]["apiKey"],
        base_url=settings["ai"]["defaultBaseUrl"]
    )
    
    channel_names = model.generate_channels(data.prompt)
    
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "channelNames": channel_names
        }
    )


__all__: list[str] = ["router"]
