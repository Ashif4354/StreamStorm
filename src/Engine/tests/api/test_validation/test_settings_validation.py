"""
Test validation for settings-related endpoints:
- AIProviderKeyData (POST /settings/ai/keys/{provider})
- SetDefaultProviderData (POST /settings/ai/default)
- GeneralSettingsData (POST /settings/general)
"""
from typing import NoReturn
from json import load
from logging import Logger, getLogger

from fastapi.testclient import TestClient
from fastapi.responses import Response
from pytest import mark
from pytest_mock import MockerFixture


logger: Logger = getLogger(f"tests.{__name__}")

with open("tests/api/test_validation/data.json", "r") as f:
    data: dict = load(f)

    ai_provider_key_data: list = data["ai_provider_key_data"]
    set_default_provider_data: list = data["set_default_provider_data"]
    general_settings_data: list = data["general_settings_data"]


@mark.parametrize("data", ai_provider_key_data)
def test_ai_provider_key_validation(mocker: MockerFixture, client: TestClient, assets_for_tests_dir, data: dict) -> NoReturn:
    """Test validation for POST /settings/ai/keys/{provider}"""
    
    logger.debug("DATA ID: %s", data["id"])
    del data["id"]
    
    result: int = data["result"]
    del data["result"]
    
    # Mock settings file path
    mocker.patch("lib.settings.Settings.SETTINGS_FILE_PATH", assets_for_tests_dir / "settings.json")
    
    response: Response = client.post("/settings/ai/keys/openai", json=data)
    logger.debug(response.json())
    
    assert response.status_code == result


@mark.parametrize("data", set_default_provider_data)
def test_set_default_provider_validation(mocker: MockerFixture, client: TestClient, assets_for_tests_dir, data: dict) -> NoReturn:
    """Test validation for POST /settings/ai/default"""
    
    logger.debug("DATA ID: %s", data["id"])
    del data["id"]
    
    result: int = data["result"]
    del data["result"]
    
    # Mock settings file path
    mocker.patch("lib.settings.Settings.SETTINGS_FILE_PATH", assets_for_tests_dir / "settings.json")
    
    response: Response = client.post("/settings/ai/default", json=data)
    logger.debug(response.json())
    
    assert response.status_code == result


@mark.parametrize("data", general_settings_data)
def test_general_settings_validation(client: TestClient, data: dict) -> NoReturn:
    """Test validation for POST /settings/general"""
    
    logger.debug("DATA ID: %s", data["id"])
    del data["id"]
    
    result: int = data["result"]
    del data["result"]
    
    response: Response = client.post("/settings/general", json=data)
    logger.debug(response.json())
    
    assert response.status_code == result
