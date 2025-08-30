from re import A
from typing import NoReturn

from unittest.mock import MagicMock, AsyncMock
from  pytest_mock import MockerFixture

from fastapi.testclient import TestClient
from fastapi.responses import Response

from StreamStorm.api.fastapi_app import app

client: TestClient = TestClient(app)

def test_root() -> NoReturn:

    response: Response = client.get("/")

    assert response.status_code == 200
    
def test_get_ram_info() -> NoReturn:

    response: Response = client.get("/get_ram_info")

    assert response.status_code == 200
    
def test_engine_status() -> NoReturn:

    response: Response = client.get("/engine-status")

    assert response.status_code == 200

def test_start(mocker: MockerFixture) -> NoReturn:
    
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
    
    assert response.status_code == 200
    assert response.json()["success"]
    
    mock_start.assert_called_once()

def test_stop() -> NoReturn:

    response: Response = client.post("/storm/stop")

    assert response.status_code == 200

def test_pause() -> NoReturn:

    response: Response = client.post("/storm/pause")

    assert response.status_code == 409
    
def test_resume() -> NoReturn:

    response: Response = client.post("/storm/resume")

    assert response.status_code == 409
    
def test_change_messages() -> NoReturn:

    response: Response = client.post("/storm/change_messages")

    assert response.status_code == 409
    
def test_start_storm_dont_wait() -> NoReturn:

    response: Response = client.post("/storm/start_storm_dont_wait")

    assert response.status_code == 409

def test_change_slow_mode() -> NoReturn:

    response: Response = client.post("/storm/change_slow_mode")

    assert response.status_code == 409
    
def test_start_more_channels() -> NoReturn:

    response: Response = client.post("/storm/start_more_channels")

    assert response.status_code == 409
    
def test_get_channels_data() -> NoReturn:
    
    data: dict = {"mode": "add"}

    response: Response = client.post("/storm/get_channels_data", json=data)

    assert response.status_code == 400
    
    
def test_create_profiles(mocker: MockerFixture) -> NoReturn:
    
    mocker.patch("StreamStorm.api.routers.ProfileRouter.run_in_threadpool", new=AsyncMock())
    
    data: dict = {"count": 1}

    response: Response = client.post("/profiles/create_profiles", json=data)

    assert response.status_code == 200
    
def test_delete_all_profiles(mocker: MockerFixture) -> NoReturn:
    
    data: dict = {}
    
    mocker.patch("StreamStorm.api.routers.ProfileRouter.run_in_threadpool", new = AsyncMock())
    
    response: Response = client.post("/profiles/delete_all_profiles", json=data)

    assert response.status_code == 200