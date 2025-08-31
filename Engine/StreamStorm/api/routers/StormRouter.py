from logging import getLogger, Logger
from os import environ
from os.path import join, exists
from json import JSONDecodeError, loads
from asyncio import gather

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from platformdirs import user_data_dir
from aiofiles import open as aio_open

from ...core.StreamStorm import StreamStorm
from ..validation import (
    StormData,
    ChangeMessagesData,
    ChangeSlowModeData,
    StartMoreChannelsData,
    GetChannelsData
)

logger: Logger = getLogger("fastapi." + __name__)

router: APIRouter = APIRouter(prefix="/storm")

@router.post("/start")
async def start(data: StormData) -> JSONResponse:
    if StreamStorm.ss_instance is not None:
        logger.info("Storm request rejected - instance already running")
        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "message": "A storm is already running. Stop the current storm before starting a new one.",
            }
        )

    StreamStorm.each_channel_instances = []

    StreamStormObj: StreamStorm = StreamStorm(
        data.video_url,
        data.chat_url,
        data.messages,
        (data.subscribe, data.subscribe_and_wait),
        data.subscribe_and_wait_time,
        data.slow_mode,
        data.channels,
        data.background
    )

    StreamStormObj.ready_event.clear()  # Clear the ready event to ensure it will be only set when all instances are ready
    StreamStormObj.pause_event.set()  # Set the pause event to allow storming to start immediately
    StreamStormObj.run_stopper_event.clear()  # Clear the run stopper event to wait for instances to be ready before starting

    environ.update({"BUSY": "1", "BUSY_REASON": "Storming in progress"})
    logger.debug("Environment updated to BUSY state")

    try:
        await StreamStormObj.start()
    except SystemError as e:
        environ.update({"BUSY": "0", "BUSY_REASON": ""})
        StreamStorm.ss_instance = None
        raise e

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Storm started successfully"
        }
    )


@router.post("/stop")
async def stop() -> JSONResponse:
    async def close_browser(instance: StreamStorm) -> None:
        try:
            if instance.page:
                await instance.page.close()
        except Exception:
            pass # log.warn

    await gather(*(close_browser(i) for i in StreamStorm.each_channel_instances))

    StreamStorm.ss_instance = None

    environ.update({"BUSY": "0"})

    return JSONResponse(
        status_code=200,
        content={
            "success": True, 
            "message": "Storm stopped successfully"
        }
    )


@router.post("/pause")
async def pause() -> JSONResponse:
    StreamStorm.ss_instance.pause_event.clear()

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Storm paused successfully"
        }
    )


@router.post("/resume")
async def resume() -> JSONResponse:
    StreamStorm.ss_instance.pause_event.set()

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Storm resumed successfully"
        }
    )


@router.post("/change_messages")
async def change_messages(data: ChangeMessagesData) -> JSONResponse:
    await StreamStorm.ss_instance.set_messages(data.messages)

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Messages changed successfully"
        }
    )


@router.post("/start_storm_dont_wait")
async def start_storm_dont_wait() -> JSONResponse:
    StreamStorm.ss_instance.ready_event.set()

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Storm started without waiting for all instances to be ready",
        }
    )


@router.post("/change_slow_mode")
async def change_slow_mode(data: ChangeSlowModeData) -> JSONResponse:
    if not StreamStorm.ss_instance.ready_event.is_set():
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Cannot change slow mode before the storm starts",
            }
        )

    await StreamStorm.ss_instance.set_slow_mode(data.slow_mode)

    return JSONResponse(
        status_code=200,
        content={
            "success": True, 
            "message": "Slow mode changed successfully"
        }
    )


@router.post("/start_more_channels")
async def start_more_channels(data: StartMoreChannelsData) -> JSONResponse:
    if not StreamStorm.ss_instance.ready_event.is_set():
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Cannot start more channels before the storm starts",
            }
        )

    await StreamStorm.ss_instance.start_more_channels(data.channels)

    return JSONResponse(
        status_code=200,
        content={
            "success": True, 
            "message": "More channels started successfully"
        }
    )
    
@router.post("/get_channels_data")
async def get_channels_data(data: GetChannelsData) -> JSONResponse:
    mode: str = data.mode

    if mode == "add" and StreamStorm.ss_instance is None:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "No storm is running. Start a storm first.",
            }
        )

    app_data_dir: str = user_data_dir("StreamStorm", "DarkGlance")
    config_json_path: str = join(app_data_dir, "ChromiumProfiles", "config.json")

    if not exists(config_json_path):
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": "Config file not found. Create profiles first.",
            }
        )

    try:
        async with aio_open(config_json_path, "r", encoding="utf-8") as file:
            config: dict = loads(await file.read())
    except (FileNotFoundError, PermissionError, UnicodeDecodeError, JSONDecodeError) as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error reading config file: {str(e)}",
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error parsing config file: {str(e)}",
            }
        )

    response_data: dict = {}

    if mode == "new":
        response_data["channels"] = config["channels"]
        response_data["activeChannels"] = []

    elif mode == "add":
        active_channels: list[str] = await StreamStorm.ss_instance.get_active_channels()

        response_data["channels"] = config["channels"]
        response_data["activeChannels"] = active_channels

    response_data.update({"success": True})

    return JSONResponse(
        status_code=200,
        content=response_data
    )