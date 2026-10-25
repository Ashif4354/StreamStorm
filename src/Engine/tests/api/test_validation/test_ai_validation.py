"""
Test validation for AI-related endpoints:
- GenerateMessagesRequest (POST /ai/generate/messages)
- GenerateMessagesRequest (POST /ai/generate/channel-names)
"""
from typing import NoReturn
from json import load
from logging import Logger, getLogger
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient
from fastapi.responses import Response
from pytest import mark, raises
from pytest_mock import MockerFixture

from lib.ai.PydanticAI import PydanticAI
from lib.settings import settings
from lib.settings.SavedSettings import AISettings


logger: Logger = getLogger(f"tests.{__name__}")

with open("tests/api/test_validation/data.json", "r") as f:
    data: dict = load(f)

    generate_messages_request_data: list = data["generate_messages_request_data"]


@mark.parametrize("data", generate_messages_request_data)
def test_generate_messages_validation(mocker: MockerFixture, client: TestClient, data: dict) -> NoReturn:
    """Test validation for POST /ai/generate/messages"""
    
    data = data.copy()
    
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


def test_pydantic_ai_raises_system_error_when_unconfigured(mocker: MockerFixture, client: TestClient) -> None:
    """When defaultProvider/defaultModel are None, PydanticAI() raises SystemError (400 response)."""
    mocker.patch.object(settings, "ai", AISettings())

    with raises(SystemError, match="Default AI provider and model are not configured"):
        PydanticAI()

    response: Response = client.post("/ai/generate/messages", json={"prompt": "hi"})
    assert response.status_code == 400
    assert response.json()["success"] is False


def test_pydantic_ai_reads_runtime_updated_settings(mocker: MockerFixture) -> None:
    """PydanticAI() resolves settings.ai dynamically at call time rather than import time."""
    ai_settings = AISettings(defaultProvider="google", defaultModel="gemini-2.5-flash")
    ai_settings.providers.google.apiKey = "test-google-key"
    mocker.patch.object(settings, "ai", ai_settings)

    mock_get_model = mocker.patch("lib.ai.PydanticAI.ModelFactory.get_model", return_value=MagicMock())

    PydanticAI()

    mock_get_model.assert_called_once_with(
        "google",
        model_name="gemini-2.5-flash",
        api_key="test-google-key",
        base_url=None,
    )


def test_pydantic_ai_raises_system_error_when_api_key_missing(mocker: MockerFixture) -> None:
    """When provider API key is empty, PydanticAI() raises SystemError."""
    ai_settings = AISettings(defaultProvider="openai", defaultModel="gpt-4o-mini")
    ai_settings.providers.openai.apiKey = ""
    mocker.patch.object(settings, "ai", ai_settings)

    with raises(SystemError, match="API key for openai is not configured"):
        PydanticAI()
