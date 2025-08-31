from typing import NoReturn
from json import load
from logging import Logger, getLogger

from pytest import mark

from fastapi.testclient import TestClient
from fastapi.responses import Response

logger: Logger = getLogger("tests." + __name__)

with open("tests/api/test_validation/data.json", "r") as f:
    data: dict = load(f)
    
    valid_data: list = data["storm_data"]["valid_data"]
    invalid_data: list = data["storm_data"]["invalid_data"]
    missing_data: list = data["storm_data"]["missing_data"]
    

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