from typing import NoReturn
from logging import Logger, getLogger
from pathlib import Path 

from unittest.mock import MagicMock, AsyncMock, PropertyMock
from pytest_mock import MockerFixture

from fastapi.testclient import TestClient
from fastapi.responses import Response

logger: Logger = getLogger(f"tests.{__name__}")

def test_root(client: TestClient) -> NoReturn:

    response: Response = client.get("/")
    logger.debug(response.json())

    assert response.status_code == 200
    

def test_get_ram_info(client: TestClient) -> NoReturn:

    response: Response = client.get("/get_ram_info")
    logger.debug(response.json())

    assert response.status_code == 200
    

def test_start_storm(mocker: MockerFixture, client: TestClient) -> NoReturn:
    
    mock_start: MagicMock = mocker.patch("lib.core.StreamStorm.StreamStorm.start", new_callable=AsyncMock)

    test_payload: dict = {
        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "chat_url": "https://www.youtube.com/live_chat?v=dQw4w9WgXcQ",
        "messages": ["Never gonna give you up"],
        "subscribe": False,
        "subscribe_and_wait": False,
        "subscribe_and_wait_time": 70,
        "slow_mode": 5,
        "channels": [1, 2],
        "background": True
    }

    response: Response = client.post("/storm/start", json=test_payload)
    logger.debug(response.json())
    
    assert response.status_code == 200
    assert response.json()["success"]
    
    mock_start.assert_called_once()


def test_stop(client: TestClient) -> NoReturn:

    response: Response = client.post("/storm/stop")
    logger.debug(response.json())

    assert response.status_code == 200


def test_pause(client: TestClient) -> NoReturn:

    response: Response = client.post("/storm/pause")
    logger.debug(response.json())

    assert response.status_code == 409


def test_resume(client: TestClient) -> NoReturn:

    response: Response = client.post("/storm/resume")
    logger.debug(response.json())

    assert response.status_code == 409


def test_change_messages(client: TestClient) -> NoReturn:

    response: Response = client.post("/storm/change_messages")
    logger.debug(response.json())

    assert response.status_code == 409


def test_start_storm_dont_wait(client: TestClient) -> NoReturn:

    response: Response = client.post("/storm/start_storm_dont_wait")
    logger.debug(response.json())

    assert response.status_code == 409


def test_change_slow_mode(client: TestClient) -> NoReturn:

    response: Response = client.post("/storm/change_slow_mode")
    logger.debug(response.json())

    assert response.status_code == 409


def test_start_more_channels(client: TestClient) -> NoReturn:

    response: Response = client.post("/storm/start_more_channels")
    logger.debug(response.json())

    assert response.status_code == 409


def test_get_channels_data(client: TestClient) -> NoReturn:
    
    data: dict = {"mode": "add"}

    response: Response = client.post("/storm/get_channels_data", json=data)
    logger.debug(response.json())

    assert response.status_code == 400
    
    
def test_create_profiles(mocker: MockerFixture, client: TestClient) -> NoReturn:
    
    new_run_in_threadpool: AsyncMock = mocker.patch("lib.api.routers.ProfileRouter.run_in_threadpool", new=AsyncMock())
    
    data: dict = {"count": 1}

    response: Response = client.post("/environment/profiles/create", json=data)
    logger.debug(response.json())

    assert response.status_code == 200    
    new_run_in_threadpool.assert_called_once()


def test_delete_all_profiles(mocker: MockerFixture, client: TestClient) -> NoReturn:
    
    
    new_run_in_threadpool: AsyncMock = mocker.patch("lib.api.routers.ProfileRouter.run_in_threadpool", new = AsyncMock())
    
    response: Response = client.post("/environment/profiles/delete")
    logger.debug(response.json())

    assert response.status_code == 200    
    new_run_in_threadpool.assert_called_once()


def test_get_storm(client: TestClient) -> NoReturn:
    
    response: Response = client.get("/storm")
    logger.debug(response.json())

    assert response.status_code == 200


def test_kill_instance(client: TestClient) -> NoReturn:
    
    data: dict = {"index": 1, "name": "MrBeast"}

    response: Response = client.post("/storm/kill_instance", json=data)
    logger.debug(response.json())

    assert response.status_code == 409


def test_get_context(client: TestClient) -> NoReturn:
    
    response: Response = client.get("/storm/context")
    logger.debug(response.json())

    assert response.status_code == 409


def test_save_cookies(mocker: MockerFixture, client: TestClient) -> NoReturn:
    
    response: Response = client.post("/environment/profiles/save_cookies", files={"files": ""})
    logger.debug(response.json())

    assert response.status_code == 400


def test_create_channels(mocker: MockerFixture, client: TestClient, settings) -> NoReturn:

    mocker.patch.object(
        type(settings), 
        "is_logged_in", 
        new_callable=PropertyMock, 
        return_value=False
    )

    data: dict = {
        "channels": [
            {
                "name": "MrBeast",
                "uri": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
        ],
        "logo_needed": True,
        "random_logo": True
    }

    response: Response = client.post("/environment/channels/create", json=data)
    logger.debug(response.json())

    assert response.status_code == 401


def test_verify_channels_logo_dir(client: TestClient) -> NoReturn:

    data: dict = {
        "directory": ""
    }

    response: Response = client.post("/environment/channels/verify_dir", json=data)
    logger.debug(response.json())

    assert response.status_code == 400
    

def test_save_settings(client: TestClient) -> NoReturn:
    
    data: dict = {
        "login_method": "profiles"
    }

    response: Response = client.post("/settings/general", json=data)
    logger.debug(response.json())

    assert response.status_code == 200


def test_clear_login_data(client: TestClient, mocker: MockerFixture) -> NoReturn:

    mocker.patch("lib.api.routers.SettingsRouter.settings.environment_dir", Path("non_existent_dir"))
    
    response: Response = client.delete("/settings/general/clear-login-data")
    logger.debug(response.json())

    assert response.status_code == 200


def test_get_settings(client: TestClient) -> NoReturn:
    
    response: Response = client.get("/settings")
    logger.debug(response.json())

    assert response.status_code == 200


def test_get_ai_keys(client: TestClient) -> NoReturn:
    
    response: Response = client.get("/settings/ai/keys")
    logger.debug(response.json())

    assert response.status_code == 200


def test_save_api_keys(client: TestClient, mocker: MockerFixture, assets_for_tests_dir) -> NoReturn:
    
    mocker.patch("lib.settings.Settings.SETTINGS_FILE_PATH", assets_for_tests_dir / "settings.json")

    data: dict = {
        "api_key": "**********",
        "model": "gpt-4o"
    }
    
    response: Response = client.post("/settings/ai/keys/openai", json=data)
    logger.debug(response.json())

    assert response.status_code == 200


def test_save_default_provider(client: TestClient, mocker: MockerFixture, assets_for_tests_dir) -> NoReturn:

    mocker.patch("lib.settings.Settings.SETTINGS_FILE_PATH", assets_for_tests_dir / "settings.json")

    data: dict = {
        "provider": "openai",
        "api_key": "**********",
        "model": "gpt-4o",
        "base_url": "https://api.openai.com/v1"
    }
    
    response: Response = client.post("/settings/ai/default", json=data)
    logger.debug(response.json())

    assert response.status_code == 200


def test_generate_messages(client: TestClient, mocker: MockerFixture) -> NoReturn:
    
    # Mock the return value of the generate_messages method
    mock_ai_instance = AsyncMock()
    mock_ai_instance.generate_messages.return_value = ["Message 1", "Message 2"]
    
    # Patch the PydanticAI class to return our mock instance
    mocker.patch("lib.api.routers.AIRouter.PydanticAI", return_value=mock_ai_instance)
    
    data: dict = {
        "prompt": "Generate 10 messages"
    }

    response: Response = client.post("/ai/generate/messages", json=data)
    logger.debug(response.json())

    assert response.status_code == 200


def test_generate_channel_names(client: TestClient, mocker: MockerFixture) -> NoReturn:
    
    # Mock the return value of the generate_channels method
    mock_ai_instance = AsyncMock()
    mock_ai_instance.generate_channels.return_value = ["Channel 1", "Channel 2"]
    
    # Patch the PydanticAI class to return our mock instance
    mocker.patch("lib.api.routers.AIRouter.PydanticAI", return_value=mock_ai_instance)
    
    data: dict = {
        "prompt": "Generate 10 channel names"
    }

    response: Response = client.post("/ai/generate/channel-names", json=data)
    logger.debug(response.json())

    assert response.status_code == 200