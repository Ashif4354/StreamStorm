from typing import NoReturn
from logging import Logger, getLogger

from unittest.mock import AsyncMock
from pytest import mark
from pytest_mock import MockerFixture

from fastapi import Response
from fastapi.testclient import TestClient

logger: Logger = getLogger("tests." + __name__)

COUNT_VALUES: tuple[tuple[int, int], ...] = (
    (-1, 422),
    (0, 422),
    (1, 200),
    (3, 200),
    (None, 422),
    ("string", 422),
    (1.0, 422),
    (1.5, 422),
    (True, 422),
    (False, 422),
    ({}, 422),
    ([], 422)  
)


@mark.parametrize("count, expected", COUNT_VALUES)
def test_data_validation_create_profiles(mocker: MockerFixture, client: TestClient, count: int, expected: int) -> NoReturn:
    
    mocker.patch("StreamStorm.api.routers.ProfileRouter.run_in_threadpool", new=AsyncMock())
    
    response: Response = client.post("/profiles/create_profiles", json={"count": count})
    logger.debug(response.json())
    
    assert response.status_code == expected
    