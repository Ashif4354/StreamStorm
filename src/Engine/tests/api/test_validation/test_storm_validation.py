from typing import NoReturn
from json import load
from pathlib import Path
from logging import Logger, getLogger
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
from pytest import MonkeyPatch, mark
from pytest_mock import MockerFixture

from fastapi.responses import Response
from lib.core.StreamStorm import StreamStorm


logger: Logger = getLogger(f"tests.{__name__}")

with open("tests/api/test_validation/data.json", "r") as f:
    data: dict = load(f)

    valid_data: list = data["storm_data"]["valid_data"]
    invalid_data: list = data["storm_data"]["invalid_data"]
    missing_data: list = data["storm_data"]["missing_data"]
    change_messages_data: list = data["change_messages_data"]
    change_slow_mode_data: list = data["change_slow_mode_data"]
    start_more_channels_data: list = data["start_more_channels_data"]
    get_channels_data: list = data["get_channels_data"]
    

@mark.parametrize("data", valid_data)
def test_data_validation_storm_with_valid_data(client: TestClient, data: dict) -> NoReturn:
    logger.debug("DATA ID: %s", data["id"])
    del data["id"]

    response: Response = client.post("/storm/start", json=data)
    logger.debug(response.json())    

    assert response.status_code == 200
    

@mark.parametrize("data", missing_data)
def test_data_validation_storm_with_missing_data(client: TestClient, data: dict) -> NoReturn:
    logger.debug("DATA ID: %s", data["id"])
    del data["id"]

    response: Response = client.post("/storm/start", json=data)   
    logger.debug(response.json()) 

    assert response.status_code == 422
    
    
@mark.parametrize("data", invalid_data)
def test_data_validation_storm_with_invalid_data(client: TestClient, data: dict) -> NoReturn:
    logger.debug("DATA ID: %s", data["id"])
    del data["id"]

    response: Response = client.post("/storm/start", json=data)    
    logger.debug(response.json()) 

    assert response.status_code == 422    
    
    
@mark.parametrize("data", change_messages_data)
def test_change_messages(ss_instance: StreamStorm, client: TestClient, data: dict) -> NoReturn:
    
    logger.debug("DATA ID: %s", data["id"])
    del data["id"]
    
    result: int = data["result"]
    del data["result"]    
    
    response: Response = client.post("/storm/change_messages", json=data)
    logger.debug(response.json())

    assert response.status_code == result
    
    
@mark.parametrize("data", change_slow_mode_data)
def test_change_slow_mode(ss_instance: StreamStorm, client: TestClient, data: dict) -> NoReturn:
    
    logger.debug("DATA ID: %s", data["id"])
    del data["id"]
    
    result: int = data["result"]
    del data["result"] 
    
    ss_instance.ready_event.set()  
        
    response: Response = client.post("/storm/change_slow_mode", json=data)
    logger.debug(response.json())

    assert response.status_code == result
    
    
@mark.parametrize("data", start_more_channels_data)
def test_start_more_channels(mocker: MockerFixture, ss_instance: StreamStorm, client: TestClient, data: dict) -> NoReturn:
    mocker.patch("lib.api.routers.StormRouter.StreamStorm.start", new=AsyncMock())
    
    logger.debug("DATA ID: %s", data["id"])
    del data["id"]
    
    result: int = data["result"]
    del data["result"]    
    
    ss_instance.ready_event.set()
    
    response: Response = client.post("/storm/start_more_channels", json=data)
    logger.debug(response.json())

    assert response.status_code == result
    
    
@mark.parametrize("data", get_channels_data)
def test_get_channels_data(monkeypatch: MonkeyPatch, ss_instance: StreamStorm, client: TestClient, data: dict) -> NoReturn:
    
    logger.debug("DATA ID: %s", data["id"])
    del data["id"]
    
    result: int = data["result"]
    del data["result"]    
    
    if result == 200:
        from lib.api.routers import StormRouter
        # assets_dir: str = join(abspath("."), "tests", "assets_for_tests")
        data_json_path: str = Path(__file__).parent.parent.parent.resolve() / "assets_for_tests" / "Environment" / "data.json"
        
        monkeypatch.setattr(StormRouter.settings, "data_json_path", data_json_path)
    
    response: Response = client.post("/storm/get_channels_data", json=data)
    logger.debug(response.json())

    assert response.status_code == result
