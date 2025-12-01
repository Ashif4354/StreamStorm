from unittest.mock import MagicMock, AsyncMock
from pytest import MonkeyPatch, fixture
from pytest_mock import MockerFixture

from StreamStorm.core.StreamStorm import StreamStorm
from StreamStorm.api.validation import StormData


@fixture(autouse=True)
def path_storm_endpoint(mocker: MockerFixture, monkeypatch: MonkeyPatch  ):
    mocker.patch("StreamStorm.api.routers.StormRouter.StreamStorm.ss_instance", None)
    mocker.patch("StreamStorm.api.routers.StormRouter.environ.update", new=MagicMock())
    mocker.patch("StreamStorm.api.routers.StormRouter.StreamStorm.start", new=AsyncMock())
    mocker.patch("StreamStorm.api.routers.StormRouter.StreamStorm.start_more_channels", new=AsyncMock())
    
    monkeypatch.setenv("BUSY", "0")
    
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
    