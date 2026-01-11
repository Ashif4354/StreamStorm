from typing import NoReturn
from asyncio import sleep
from logging import getLogger, Logger

from ..core.StreamStorm import StreamStorm
from ..core.EngineContext import EngineContext
from ..socketio.sio import sio

logger: Logger = getLogger(f"streamstorm.{__name__}")

async def background_storm_stopper() -> NoReturn:
    """
    This function is used to stop the storming process if all the instances are dead.
    It runs in the background and checks the status of each instance every 5 seconds.
    If all instances are dead, it emits that the storm is not running.
    """
    while True:
        try:
            await sleep(5)
            
            if StreamStorm.ss_instance is None:
                continue
            
            await StreamStorm.ss_instance.run_stopper_event.wait()
            
            statuses: list[bool] = [await instance.is_instance_alive() for instance in StreamStorm.ss_instance.context.each_channel_instances.copy()]
            
            if not len(statuses):
                logger.debug("StreamStorm instance is marked dead by: Status length checker")

            if not any(statuses):
                logger.debug("Resetting StreamStorm instance and clearing each channel instances")
                StreamStorm.ss_instance.context.each_channel_instances.clear()
                StreamStorm.ss_instance = None
                EngineContext.reset()
                
                await sio.emit('storm_stopped', room="streamstorm")                
                
        except Exception as e:
            logger.error(f"Error occurred in background_storm_stopper: {e}")

__all__: list[str] = ["background_storm_stopper"]