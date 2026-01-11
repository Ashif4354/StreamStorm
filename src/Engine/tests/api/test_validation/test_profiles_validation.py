from typing import NoReturn
from logging import Logger, getLogger

from unittest.mock import AsyncMock
from pytest import mark
from pytest_mock import MockerFixture

from fastapi import Response
from fastapi.testclient import TestClient

logger: Logger = getLogger(f"tests.{__name__}")


COUNT_VALUES: tuple[tuple[int, bool, int], ...] = (
    (-1, False, 422),
    (0, False, 422),
    (1, False, 200),
    (3, False, 200),
    (None, True, 200), # Cookie login
    (None, False, 422), 
    ("string", False, 422),
    (1.0, False, 422),
    (1.5, False, 422),
    (True, False, 422),
    (False, False, 422),
    ({}, False, 422),
    ([], False, 422)  
)


@mark.parametrize("count, cookies_login, expected", COUNT_VALUES)
def test_data_validation_create_profiles(mocker: MockerFixture, client: TestClient, count: int, cookies_login: bool, expected: int) -> NoReturn:
    
    new_run_in_threadpool: AsyncMock = mocker.patch("lib.api.routers.ProfileRouter.run_in_threadpool", new=AsyncMock())
    
    response: Response = client.post("/environment/profiles/create", json={"count": count, "cookies_login": cookies_login})
    logger.debug(response.json())
    
    assert response.status_code == expected
    
    if expected == 200:
        new_run_in_threadpool.assert_called_once()
    