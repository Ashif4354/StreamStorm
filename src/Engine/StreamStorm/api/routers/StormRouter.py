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
    GetChannelsData,
    KillInstanceData
)
from ...utils.CustomLogger import CustomLogger
from ...socketio.sio import sio

cl: CustomLogger = CustomLogger(for_history=True)
cl.setup_history_logger()

logger: Logger = getLogger(f"fastapi.{__name__}")

router: APIRouter = APIRouter(prefix="/storm")

@router.post("/start")
async def start(data: StormData) -> JSONResponse:
    if StreamStorm.ss_instance is not None:
        logger.error("Storm request rejected - instance already running")
        cl.log_to_history(data, "Storm request rejected - instance already running")
        
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
        data.channels,
        (data.subscribe, data.subscribe_and_wait),
        data.subscribe_and_wait_time,
        data.slow_mode,
        data.background
    )

    StreamStormObj.ready_event.clear()  # Clear the ready event to ensure it will be only set when all instances are ready
    StreamStormObj.pause_event.set()  # Set the pause event to allow storming to start immediately
    StreamStormObj.run_stopper_event.clear()  # Clear the run stopper event to wait for instances to be ready before starting

    environ.update({"BUSY": "1", "BUSY_REASON": "Storming in progress"})
    logger.debug("Environment updated to BUSY state")

    try:
        await StreamStormObj.start()
        cl.log_to_history(data, "Storm started successfully")
        logger.info("Storm started successfully")
        
    except SystemError as e:
        environ.update({"BUSY": "0", "BUSY_REASON": ""})
        StreamStorm.ss_instance = None
        cl.log_to_history(data, "Storm failed to start")
        
        logger.error(f"Storm failed to start: SystemError: {e}")
        raise e
    
    except Exception as e:
        environ.update({"BUSY": "0", "BUSY_REASON": ""})
        cl.log_to_history(data, "Storm failed to start")
        
        logger.error(f"Storm failed to start: Exception: {e}")
        raise e   


    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Storm started successfully",
            "channels": StreamStormObj.all_channels
        }
    )


@router.post("/stop")
async def stop() -> JSONResponse:
    logger.info("Stopping Storm...")
    
    async def close_browser(instance: StreamStorm) -> None:
        try:
            if instance.page:
                await instance.page.close()
                
        except Exception as e:
            logger.error(f"Error occurred while closing browser: {e}")

    await gather(*(close_browser(i) for i in StreamStorm.each_channel_instances))

    StreamStorm.ss_instance = None

    environ.update({"BUSY": "0"})

    logger.info("Storm stopped successfully")
    await sio.emit('storm_stopped', room="streamstorm")
    

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
    logger.info("Storm paused successfully")
    await sio.emit('storm_paused', room="streamstorm")

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
    logger.info("Storm resumed successfully")
    await sio.emit('storm_resumed', room="streamstorm")

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
    logger.info("Messages changed successfully")

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
    logger.info("Storm started without waiting")

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
    logger.info("Slow mode changed successfully")

    return JSONResponse(
        status_code=200,
        content={
            "success": True, 
            "message": "Slow mode changed successfully"
        }
    )


@router.post("/start_more_channels")
async def start_more_channels(data: StartMoreChannelsData) -> JSONResponse:
    logger.info("Starting more channels...")
    if not StreamStorm.ss_instance.ready_event.is_set():
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Cannot start more channels before the storm starts",
            }
        )

    await StreamStorm.ss_instance.start_more_channels(data.channels)
    logger.info("More channels started successfully")

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
    config_json_path: str = join(app_data_dir, "ChromiumProfiles", "data.json")

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
        logger.error(f"Error reading config file: {config_json_path}: {e}")
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error reading config file, Try creating profiles again: {str(e)}",
            }
        )
    except Exception as e:
        logger.error(f"Error parsing config file: {e}")
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error parsing config file, Try creating profiles again: {str(e)}",
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

    response_data["success"] = True

    return JSONResponse(
        status_code=200,
        content=response_data
    )

@router.post("/kill_instance")
async def kill_instance(data: KillInstanceData) -> JSONResponse:
    
    try:
        for instance in StreamStorm.each_channel_instances:
            if instance.index == data.index and instance.page:
                await instance.page.close()
                
                StreamStorm.each_channel_instances.remove(instance)
                await sio.emit('instance_status', {'instance': str(data.index), 'status': '-1'}, room="streamstorm")  # -1 = Idle
                
                logger.info(f"Instance {data.index}. {data.name} killed successfully")

                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": "Instance killed successfully",
                    }
                )
              
        # await sio.emit('instance_status', {'instance': str(data.index), 'status': '-1'}, room="streamstorm")  # -1 = Idle
        
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": "Instance not found or not storming",
            }
        )
        
    except Exception as e:
        logger.error(f"Error killing instance: {e}")

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error killing instance: {str(e)}",
            }
        )
        
        
@router.get("/start_time")
async def get_storm_start_time() -> JSONResponse:

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "start_time": StreamStorm.ss_instance.start_time
        }
    )
