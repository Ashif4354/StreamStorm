from logging import Logger, getLogger

from fastapi import Response
from pytest import fixture
from pytest_mock import MockerFixture

from fastapi.testclient import TestClient

logger: Logger = getLogger("tests." + __name__)

@fixture(autouse=True)
def set_ss_instance(mocker: MockerFixture):
    mocker.patch("StreamStorm.api.routers.StormRouter.StreamStorm.ss_instance", object())
    
    
    
def test_start_storm_on_storm_running(client: TestClient):
    
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

    assert response.status_code == 409 