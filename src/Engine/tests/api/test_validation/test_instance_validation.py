"""
Test validation for instance control endpoints:
- KillInstanceData (POST /storm/kill_instance)
"""
from typing import NoReturn
from json import load
from logging import Logger, getLogger

from fastapi.testclient import TestClient
from fastapi.responses import Response
from pytest import mark

from lib.core.StreamStorm import StreamStorm


logger: Logger = getLogger(f"tests.{__name__}")

with open("tests/api/test_validation/data.json", "r") as f:
    data: dict = load(f)

    kill_instance_data: list = data["kill_instance_data"]


@mark.parametrize("data", kill_instance_data)
def test_kill_instance_validation(ss_instance: StreamStorm, client: TestClient, data: dict) -> NoReturn:
    """Test validation for POST /storm/kill_instance"""
    
    logger.debug("DATA ID: %s", data["id"])
    del data["id"]
    
    result: int = data["result"]
    del data["result"]
    
    response: Response = client.post("/storm/kill_instance", json=data)
    logger.debug(response.json())
    
    # Valid data will return 404 (instance not found) since we don't have real instances
    # Invalid data should return 422
    if result == 200:
        assert response.status_code in [200, 404]  # 404 is OK - just means instance not found
    else:
        assert response.status_code == result
