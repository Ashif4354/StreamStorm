from typing import NoReturn
from asyncio import sleep, wait_for, TimeoutError as AsyncTimeoutError
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
            
            current_instance = StreamStorm.ss_instance
            if current_instance is None:
                continue
            
            try:
                await wait_for(current_instance.context.run_stopper_event.wait(), timeout=5)
            except AsyncTimeoutError:
                if not current_instance.context.run_stopper_event.is_set():
                    continue

            if StreamStorm.ss_instance is not current_instance:
                continue

            statuses: list[bool] = [await instance.is_instance_alive() for instance in current_instance.context.each_channel_instances.copy()]
            
            if not len(statuses):
                logger.debug("StreamStorm instance is marked dead by: Status length checker")

            if not any(statuses):
                logger.debug("Resetting StreamStorm instance and clearing each channel instances")
                await current_instance.cleanup()
                if StreamStorm.ss_instance is current_instance:
                    StreamStorm.ss_instance = None
                EngineContext.reset()
                
                await sio.emit('storm_stopped', room="streamstorm")                
                
        except Exception as e:
            logger.error(f"Error occurred in background_storm_stopper: {e}")

__all__: list[str] = ["background_storm_stopper"]