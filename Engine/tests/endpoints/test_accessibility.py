from typing import NoReturn
from logging import Logger, getLogger

from unittest.mock import MagicMock, AsyncMock
from pytest_mock import MockerFixture

from fastapi.testclient import TestClient
from fastapi.responses import Response

logger: Logger = getLogger("tests." + __name__)

def test_root(client: TestClient) -> NoReturn:

    response: Response = client.get("/")
    logger.debug(response.json())

    assert response.status_code == 200
    
def test_get_ram_info(client: TestClient) -> NoReturn:

    response: Response = client.get("/get_ram_info")
    logger.debug(response.json())

    assert response.status_code == 200
    
def test_engine_status(client: TestClient) -> NoReturn:

    response: Response = client.get("/engine-status")

    assert response.status_code == 200

def test_start_storm(mocker: MockerFixture, client: TestClient) -> NoReturn:
    
    mock_start: MagicMock = mocker.patch("StreamStorm.core.StreamStorm.StreamStorm.start", new_callable=AsyncMock)

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
    
    mocker.patch("StreamStorm.api.routers.ProfileRouter.run_in_threadpool", new=AsyncMock())
    
    data: dict = {"count": 1}

    response: Response = client.post("/profiles/create_profiles", json=data)
    logger.debug(response.json())

    assert response.status_code == 200
    
def test_delete_all_profiles(mocker: MockerFixture, client: TestClient) -> NoReturn:
    
    
    mocker.patch("StreamStorm.api.routers.ProfileRouter.run_in_threadpool", new = AsyncMock())
    
    response: Response = client.post("/profiles/delete_all_profiles")
    logger.debug(response.json())

    assert response.status_code == 200