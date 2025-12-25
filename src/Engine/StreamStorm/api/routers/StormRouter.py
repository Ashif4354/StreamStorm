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
from ...core.SeparateInstance import SeparateInstance
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

router: APIRouter = APIRouter(prefix="/storm", tags=["Manage Storms"])

@router.get("", operation_id="get_storm_status", summary="Get the current storm status.")
async def index() -> JSONResponse:
    """
    Get the current storm status.
    
    Returns whether a storm (YouTube live chat message spam) is currently running or not.
    
    Returns:
        success (bool): True if the request was successful
        storm (bool): True if a storm is currently running
        message (str): Human-readable status message
    """
    if StreamStorm.ss_instance is None:
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "storm": False,
                "message": "Storm is not running",
            }
        )
    else:
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "storm": True,
                "message": "Storm is running",
            }
        )

@router.post("/start", operation_id="start_storm", summary="Start a new YouTube live chat spam storm.")
async def start(data: StormData) -> JSONResponse:
    """
    Start a new storm (storm means spamming messages in YouTube live chat).
    
    Initializes browser instances for each channel and begins sending
    messages to the specified YouTube live chat at the configured rate.
    The available channels and their indices can be retrieved using POST /storm/get_channels_data or the get_available_channels mcp tool. with mode "new"
    
    Args:
        data.video_url (str): YouTube video URL (format: https://www.youtube.com/watch?v=VIDEO_ID)
        data.chat_url (str): YouTube live chat URL (format: https://www.youtube.com/live_chat?v=VIDEO_ID)
        data.messages (list[str]): List of messages to spam in rotation
        data.channels (list[int]): List of channel profile IDs to use for storming
        data.slow_mode (int): Delay in seconds between messages (minimum 1)
        data.subscribe (bool): Whether to subscribe to the channel before sending messages
        data.subscribe_and_wait (bool): Whether to wait after subscribing before spamming
        data.subscribe_and_wait_time (int): Time in seconds to wait after subscribing
        data.background (bool): Whether to run browsers in headless/background mode
    
    Returns:
        success (bool): True if the storm started successfully
        message (str): Confirmation message
        channels (list): List of channels that were started
    """
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

    StreamStormObj: StreamStorm = StreamStorm(data)

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


@router.post("/stop", operation_id="stop_storm", summary="Stop the currently running storm.")
async def stop() -> JSONResponse:
    """
    Stop the currently running storm.
    
    Closes all browser instances and stops sending messages to YouTube live chat.
    Emits 'storm_stopped' socket event when complete.
    
    Returns:
        success (bool): True if the storm was stopped successfully
        message (str): Confirmation message
    """
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


@router.post("/pause", operation_id="pause_storm", summary="Pause the currently running storm.")
async def pause() -> JSONResponse:
    """
    Pause the currently running storm.
    
    Temporarily stops sending messages while keeping browser instances open.
    Implements gradual pause based on slow_mode settings.
    Emits 'storm_paused' socket event when complete.
    
    Returns:
        success (bool): True if the storm was paused successfully
        message (str): Confirmation message
    """
    StreamStorm.ss_instance.pause_event.clear()
    StreamStorm.ss_instance.storm_context["storm_status"] = "Paused"

    current_channels: list[SeparateInstance] = StreamStorm.each_channel_instances
    available_profiles: int = len(StreamStorm.ss_instance.get_available_temp_profiles())
    
    for index, channel in enumerate(current_channels):
        channel.should_wait = True
        channel.wait_time = index * (StreamStorm.ss_instance.slow_mode / available_profiles)
    
    logger.info("Storm paused successfully")
    await sio.emit('storm_paused', room="streamstorm")

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Storm paused successfully"
        }
    )


@router.post("/resume", operation_id="resume_storm", summary="Resume a paused storm.")
async def resume() -> JSONResponse:
    """
    Resume a paused storm.
    
    Continues sending messages after a pause.
    Emits 'storm_resumed' socket event when complete.
    
    Returns:
        success (bool): True if the storm was resumed successfully
        message (str): Confirmation message
    """
    StreamStorm.ss_instance.pause_event.set()
    StreamStorm.ss_instance.storm_context["storm_status"] = "Running"
    
    logger.info("Storm resumed successfully")
    await sio.emit('storm_resumed', room="streamstorm")

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Storm resumed successfully"
        }
    )


@router.post("/change_messages", operation_id="change_storm_messages", summary="Change messages during an active storm.")
async def change_messages(data: ChangeMessagesData) -> JSONResponse:
    """
    Change the messages being sent in the current storm.
    
    Updates the message pool used for spamming during an active storm.
    
    Args:
        data.messages (list[str]): New list of messages to use
    
    Returns:
        success (bool): True if messages were changed successfully
        message (str): Confirmation message
    """
    await StreamStorm.ss_instance.set_messages(data.messages)
    logger.info("Messages changed successfully")

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Messages changed successfully"
        }
    )


@router.post("/start_storm_dont_wait", operation_id="start_storm_immediately", summary="Start storm without waiting for all instances.")
async def start_storm_dont_wait() -> JSONResponse:
    """
    Start the storm without waiting for all instances to be ready.
    
    Forces the storm to begin immediately even if some browser instances
    are still initializing or getting ready. Useful for faster starts with large channel counts.
    
    Returns:
        success (bool): True if the command was executed successfully
        message (str): Confirmation message
    """
    StreamStorm.ss_instance.ready_event.set()
    logger.info("Storm started without waiting")

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Storm started without waiting for all instances to be ready",
        }
    )


@router.post("/change_slow_mode", operation_id="change_storm_slow_mode", summary="Change the slow mode delay during a storm.")
async def change_slow_mode(data: ChangeSlowModeData) -> JSONResponse:
    """
    Change the slow mode interval for the current storm.
    
    Adjusts the delay between messages sent to YouTube live chat.
    Can only be changed after the storm has started.
    
    Args:
        data.slow_mode (float): New slow mode interval in seconds
    
    Returns:
        success (bool): True if slow mode was changed successfully
        message (str): Confirmation message
    """
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


@router.post("/start_more_channels", operation_id="add_channels_to_storm", summary="Add more channels to an active storm.")
async def start_more_channels(data: StartMoreChannelsData) -> JSONResponse:
    """
    Add more channels to an active storm.
    
    Starts additional browser instances for new channels while
    the storm is already running. Can only be called after storm starts and spamming has started.
    The available channels and their indices can be retrieved using POST /storm/get_channels_data or the get_available_channels mcp tool. with mode "add"
    
    Args:
        data.channels (list[str]): List of channel names to add
    
    Returns:
        success (bool): True if channels were added successfully
        message (str): Confirmation message
    """
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
    
@router.post("/get_channels_data", operation_id="get_available_channels", summary="Get available channels for starting or adding to a storm.")
async def get_channels_data(data: GetChannelsData) -> JSONResponse:
    """
    Get available channels data for starting or adding to a storm.
    
    Retrieves the list of configured channels from the profile data.
    Mode determines whether to return channels for a new storm or
    for adding to an existing storm.
    
    Args:
        data.mode (str): 'new' for new storm, 'add' for adding to existing storm
    
    Returns:
        success (bool): True if the request was successful
        channels (list): Available channel configurations
        activeChannels (list): Currently active channels (only in 'add' mode)
    """
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

@router.post("/kill_instance", operation_id="kill_storm_instance", summary="Kill a specific storm instance by index.")
async def kill_instance(data: KillInstanceData) -> JSONResponse:
    """
    Kill a specific storm instance by index.
    
    Closes the browser for a specific channel instance and removes it
    from the active storm. Emits 'instance_status' socket event with status -1.
    
    Args:
        data.index (int): Index of the instance to kill
        data.name (str): Name of the channel (for logging)
    
    Returns:
        success (bool): True if the instance was killed successfully
        message (str): Result message
    """
    
    try:
        for instance in StreamStorm.each_channel_instances:
            if instance.index == data.index and instance.page:
                await instance.page.close()
                
                StreamStorm.each_channel_instances.remove(instance)
                StreamStorm.ss_instance.total_instances -= 1
                StreamStorm.ss_instance.assigned_profiles[instance.profile_dir] = None
                
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
        
         
@router.get("/context", operation_id="get_storm_context", summary="Get the current storm context and statistics.")
async def get_context() -> JSONResponse:
    """
    Get the current storm context and statistics.
    
    Returns detailed information about the running storm including
    1. All the configure storm data received via form
    2. Status of each channels used for storm - Idle(-1), Dead(0), Getting Ready(1), Ready(2), Storming(3), 
    3. Storm Status - Running, Stopped, Paused
    4. Storm Start TIme

    Returns:
        success (bool): True if the request was successful
        context (dict): Current storm context with runtime statistics
        message (str): Confirmation message
    """
    
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "context": StreamStorm.ss_instance.storm_context,
            "message": "Context fetched successfully"
        }
    )
