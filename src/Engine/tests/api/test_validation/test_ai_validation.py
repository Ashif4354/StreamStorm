"""
Test validation for AI-related endpoints:
- GenerateMessagesRequest (POST /ai/generate/messages)
- GenerateMessagesRequest (POST /ai/generate/channel-names)
"""
from typing import NoReturn
from json import load
from logging import Logger, getLogger
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
from fastapi.responses import Response
from pytest import mark
from pytest_mock import MockerFixture


logger: Logger = getLogger(f"tests.{__name__}")

with open("tests/api/test_validation/data.json", "r") as f:
    data: dict = load(f)

    generate_messages_request_data: list = data["generate_messages_request_data"]


@mark.parametrize("data", generate_messages_request_data)
def test_generate_messages_validation(mocker: MockerFixture, client: TestClient, data: dict) -> NoReturn:
    """Test validation for POST /ai/generate/messages"""
    
    data = data.copy()  # Copy to avoid modifying shared parametrized data
    
    logger.debug("DATA ID: %s", data["id"])
    del data["id"]
    
    result: int = data["result"]
    del data["result"]
    
    # Mock the AI to avoid actual API calls
    mock_ai_instance = AsyncMock()
    mock_ai_instance.generate_messages.return_value = ["Message 1", "Message 2"]
    mocker.patch("lib.api.routers.AIRouter.PydanticAI", return_value=mock_ai_instance)
    
    response: Response = client.post("/ai/generate/messages", json=data)
    logger.debug(response.json())
    
    assert response.status_code == result


@mark.parametrize("data", generate_messages_request_data)
def test_generate_channel_names_validation(mocker: MockerFixture, client: TestClient, data: dict) -> NoReturn:
    """Test validation for POST /ai/generate/channel-names (uses same request model)"""
    
    data = data.copy()  # Copy to avoid modifying shared parametrized data
    
    logger.debug("DATA ID: %s", data["id"])
    del data["id"]
    
    result: int = data["result"]
    del data["result"]
    
    # Mock the AI to avoid actual API calls
    mock_ai_instance = AsyncMock()
    mock_ai_instance.generate_channels.return_value = ["Channel 1", "Channel 2"]
    mocker.patch("lib.api.routers.AIRouter.PydanticAI", return_value=mock_ai_instance)
    
    response: Response = client.post("/ai/generate/channel-names", json=data)
    logger.debug(response.json())
    
    assert response.status_code == result
