from re import S
from unittest.mock import AsyncMock
from pytest import fixture
from pytest_mock import MockerFixture

from fastapi.testclient import TestClient

from StreamStorm.core.StreamStorm import StreamStorm


@fixture(autouse=True)
def reset_streamstorm(mocker: MockerFixture):
    StreamStorm.ss_instance = None
    mocker.patch("StreamStorm.api.routers.StormRouter.StreamStorm.start", new=AsyncMock())
    yield
    StreamStorm.ss_instance = None


def test_storm_data_instantiated(client: TestClient):
    assert StreamStorm.ss_instance is None
    
    video_url: str = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    chat_url: str = "https://www.youtube.com/live_chat?v=dQw4w9WgXcQ"
    messages: list = ["Never gonna give you up", "Never gonna let you down"]
    subscribe: bool = False
    subscribe_and_wait: bool = False
    subscribe_and_wait_time: int = 70
    slow_mode: int = 5
    channels: list = [1, 2]
    background: bool = False

    payload: dict = {
        "video_url": video_url,
        "chat_url": chat_url,
        "messages": messages,
        "subscribe": subscribe,
        "subscribe_and_wait": subscribe_and_wait,
        "subscribe_and_wait_time": subscribe_and_wait_time,
        "slow_mode": slow_mode,
        "channels": channels,
        "background": background
    }
    
    response = client.post("/storm/start", json=payload)
    assert response.status_code == 200
    
    assert StreamStorm.ss_instance.url == video_url
    assert StreamStorm.ss_instance.chat_url == chat_url
    assert StreamStorm.ss_instance.messages == messages
    assert StreamStorm.ss_instance.subscribe == (subscribe, subscribe_and_wait)
    assert StreamStorm.ss_instance.subscribe_and_wait_time == subscribe_and_wait_time
    assert StreamStorm.ss_instance.slow_mode == slow_mode
    assert StreamStorm.ss_instance.channels == channels
    assert StreamStorm.ss_instance.background == background
    
    assert not StreamStorm.ss_instance.ready_event.is_set()
    assert StreamStorm.ss_instance.pause_event.is_set()
    assert not StreamStorm.ss_instance.run_stopper_event.is_set()
    
    assert StreamStorm.ss_instance.total_instances == len(channels)
    
    
    
    
