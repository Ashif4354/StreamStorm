from unittest.mock import MagicMock, AsyncMock
from pytest import MonkeyPatch, fixture
from pytest_mock import MockerFixture


@fixture(autouse=True)
def path_storm_endpoint(mocker: MockerFixture, monkeypatch: MonkeyPatch  ):
    mocker.patch("StreamStorm.api.routers.StormRouter.StreamStorm.ss_instance", None)
    mocker.patch("StreamStorm.api.routers.StormRouter.environ.update", new=MagicMock())
    mocker.patch("StreamStorm.api.routers.StormRouter.StreamStorm.start", new=AsyncMock())
    
    monkeypatch.setenv("rammap_path", "mock/path")