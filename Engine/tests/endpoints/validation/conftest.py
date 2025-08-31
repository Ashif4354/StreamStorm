from os import environ

from unittest.mock import MagicMock, AsyncMock
from pytest import fixture
from pytest_mock import MockerFixture

environ.update({"rammap_path": "mock/path"})

@fixture(autouse=True)
def path_storm_endpoint(mocker: MockerFixture):
    mocker.patch("StreamStorm.api.routers.StormRouter.StreamStorm.ss_instance", None)
    mocker.patch("StreamStorm.api.routers.StormRouter.environ.update", new=MagicMock())
    mocker.patch("StreamStorm.api.routers.StormRouter.StreamStorm.start", new=AsyncMock())
    
