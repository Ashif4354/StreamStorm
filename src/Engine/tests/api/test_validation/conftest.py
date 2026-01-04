from unittest.mock import AsyncMock
from pytest import fixture
from pytest_mock import MockerFixture

from lib.core.StreamStorm import StreamStorm
from lib.core.EngineContext import EngineContext
from lib.api.validation import StormData


@fixture(autouse=True)
def path_storm_endpoint(mocker: MockerFixture):
    mocker.patch("lib.api.routers.StormRouter.StreamStorm.ss_instance", None)
    mocker.patch("lib.api.routers.StormRouter.StreamStorm.start", new=AsyncMock())
    mocker.patch("lib.api.routers.StormRouter.StreamStorm.start_more_channels", new=AsyncMock())
    
    EngineContext.reset()
    
@fixture
def ss_instance():
    data = StormData(
        video_url="https://www.youtube.com/watch?v=PpQxArPYr0E",
        chat_url="https://www.youtube.com/live_chat?v=PpQxArPYr0E",
        messages=["hello", "world"],
        subscribe=False,
        subscribe_and_wait=False,
        subscribe_and_wait_time=0,
        slow_mode=5,
        channels=[1, 2],
        background=False
    )
    
    StreamStorm(data)
    
    return StreamStorm.ss_instance
    