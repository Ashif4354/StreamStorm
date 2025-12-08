from unittest.mock import MagicMock, AsyncMock
from pytest import MonkeyPatch, fixture
from pytest_mock import MockerFixture

from StreamStorm.core.StreamStorm import StreamStorm


@fixture(autouse=True)
def path_storm_endpoint(mocker: MockerFixture, monkeypatch: MonkeyPatch  ):
    mocker.patch("StreamStorm.api.routers.StormRouter.StreamStorm.ss_instance", None)
    mocker.patch("StreamStorm.api.routers.StormRouter.environ.update", new=MagicMock())
    mocker.patch("StreamStorm.api.routers.StormRouter.StreamStorm.start", new=AsyncMock())
    mocker.patch("StreamStorm.api.routers.StormRouter.StreamStorm.start_more_channels", new=AsyncMock())
    
    monkeypatch.setenv("BUSY", "0")
    
@fixture
def ss_instance():
    StreamStorm("", "", [], (False, False), 0, 0, [], False)
    
    return StreamStorm.ss_instance
    