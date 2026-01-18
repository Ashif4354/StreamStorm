from unittest.mock import patch

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
