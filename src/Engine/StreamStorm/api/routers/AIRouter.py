from logging import Logger, getLogger

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ...ai.PydanticAI import PydanticAI
from ..validation import GenerateMessagesRequest
from ...settings import settings

logger: Logger = getLogger(f"fastapi.{__name__}")

router: APIRouter = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/generate/messages", operation_id="ai_generate_messages", summary="Generate messages using AI, based on a prompt.")
async def generate_messages(data: GenerateMessagesRequest) -> JSONResponse:
    """
    Generate messages using AI, based on a prompt.
    
    Uses the configured AI provider to generate a list of messages
    suitable for YouTube live chatting based on the given prompt.
    
    Args:
        data.prompt (str): The prompt describing what kind of messages to generate and how many messages to generate
    
    Returns:
        success (bool): True if the generation was successful
        messages (list[str]): Generated messages
    """
    logger.info(f"Generating messages with prompt: {data.prompt[:50]}...")

    AI = PydanticAI()

    logger.info(f"Using provider: {settings.ai.defaultProvider}, model: {settings.ai.defaultModel}")

    messages = await AI.generate_messages(data.prompt)

    return JSONResponse(
        status_code=200, content={"success": True, "messages": messages}
    )


@router.post("/generate/channel-names", operation_id="ai_generate_channel_names", summary="Generate YouTube channel names using AI.")
async def generate_channel_names(data: GenerateMessagesRequest) -> JSONResponse:
    """
    Generate YouTube channel names using AI, based on a prompt.
    
    Uses the configured AI provider to generate creative channel names
    based on the given prompt for creating YouTube channels.
    
    Args:
        data.prompt (str): The prompt describing what kind of channel names to generate and how many channel names to generate
    
    Returns:
        success (bool): True if the generation was successful
        channelNames (list[str]): Generated channel names
    """
    logger.info(f"Generating channel names with prompt: {data.prompt[:50]}...")

    AI = PydanticAI()

    logger.info(f"Using provider: {settings.ai.defaultProvider}, model: {settings.ai.defaultModel}")
    
    channel_names = await AI.generate_channels(data.prompt)

    return JSONResponse(
        status_code=200, content={"success": True, "channelNames": channel_names}
    )


__all__: list[str] = ["router"]
