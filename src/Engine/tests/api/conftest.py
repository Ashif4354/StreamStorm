from unittest.mock import patch, PropertyMock

from pytest import fixture


@fixture(autouse=True)
def mock_get_channel_url():
    """Mock the slow get_channel_url method that uses yt-dlp network calls.
    
    This avoids slow network requests during API unit tests.
    Integration tests should NOT use this fixture.
    """
    with patch(
        "lib.core.StreamStorm.StreamStorm.get_channel_url",
        return_value=("https://mocked-channel-url", True)
    ):
        yield


@fixture(autouse=True)
def mock_logged_in():
    """Mock is_logged_in to return True for all API tests.
    
    In CI, the cookie/data files don't exist on disk, so the property
    returns False and endpoints return 401. This fixture ensures tests
    behave consistently regardless of the environment.
    """
    with patch(
        "lib.settings.Settings.Settings.is_logged_in",
        new_callable=PropertyMock,
        return_value=True
    ):
        yield


@fixture(autouse=True)
def mock_get_cookies():
    """Mock get_cookies so StreamStorm.__init__ doesn't read from disk.
    
    In CI, no cookies.json file exists. This returns valid mock cookie data.
    """
    with patch(
        "lib.core.StreamStorm.get_cookies",
        return_value=[{"name": "test", "value": "cookie"}]
    ):
        yield
