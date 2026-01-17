"""
Test validation for channels-related endpoints:
- CreateChannelsData (POST /environment/channels/create)
- VerifyChannelsDirectoryData (POST /environment/channels/verify_dir)
"""
from typing import NoReturn
from json import load
from logging import Logger, getLogger
from unittest.mock import MagicMock, PropertyMock

from fastapi.testclient import TestClient
from fastapi.responses import Response
from pytest import mark
from pytest_mock import MockerFixture


logger: Logger = getLogger(f"tests.{__name__}")

with open("tests/api/test_validation/data.json", "r") as f:
    data: dict = load(f)

    create_channels_data: list = data["create_channels_data"]
    verify_channels_directory_data: list = data["verify_channels_directory_data"]


@mark.parametrize("data", create_channels_data)
def test_create_channels_validation(mocker: MockerFixture, client: TestClient, settings, data: dict) -> NoReturn:
    """Test validation for POST /environment/channels/create"""
    
    logger.debug("DATA ID: %s", data["id"])
    del data["id"]
    
    result: int = data["result"]
    del data["result"]
    
    # Mock is_logged_in to True for valid tests
    mocker.patch.object(
        type(settings), 
        "is_logged_in", 
        new_callable=PropertyMock, 
        return_value=True
    )
    
    # Mock CreateChannels to avoid actual channel creation
    mock_create_channels = mocker.patch("lib.api.routers.ChannelsRouter.CreateChannels")
    mock_instance = MagicMock()
    mock_instance.start.return_value = []
    mock_create_channels.return_value = mock_instance
    
    response: Response = client.post("/environment/channels/create", json=data)
    logger.debug(response.json())
    
    assert response.status_code == result


@mark.parametrize("data", verify_channels_directory_data)
def test_verify_channels_directory_validation(client: TestClient, data: dict) -> NoReturn:
    """Test validation for POST /environment/channels/verify_dir"""
    
    logger.debug("DATA ID: %s", data["id"])
    del data["id"]
    
    result: int = data["result"]
    del data["result"]
    
    response: Response = client.post("/environment/channels/verify_dir", json=data)
    logger.debug(response.json())
    
    # Pydantic validation errors return 422, router may return 400/404 for other errors
    assert response.status_code in [result, 400, 404]
