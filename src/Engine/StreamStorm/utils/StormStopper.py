from typing import NoReturn
from asyncio import sleep
from logging import getLogger, Logger

from ..core.StreamStorm import StreamStorm

logger: Logger = getLogger(f"streamstorm.{__name__}")

async def background_storm_stopper() -> NoReturn:
    while True:
        try:
            await sleep(5)
            
            if StreamStorm.ss_instance is None:
                continue
            
            await StreamStorm.ss_instance.run_stopper_event.wait()
            
            statuses: list[bool] = [await instance.is_instance_alive() for instance in StreamStorm.each_channel_instances.copy()]
            
            if not len(statuses):
                logger.info("StreamStorm instance is marked dead by: Status length checker")

            if not any(statuses):
                StreamStorm.ss_instance = None
                StreamStorm.each_channel_instances.clear()
                StreamStorm.ss_instance.run_stopper_event.clear()
                
        except Exception as e:
            logger.error(f"Error occurred in background_storm_stopper: {e}")

__all__: list[str] = ["background_storm_stopper"]