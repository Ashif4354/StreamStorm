from os import getenv
from httpx import post
from typing import Any
from firebase_functions import logger

from .GetIstTime import get_ist_time


def send_discord_webhook(type_: str, count: int) -> None:
    """
    Sends a notification to a Discord webhook.
    """
    content: str = ""
    url: str = ""

    if type_ == "download":
        content = "Someone just downloaded StreamStorm!"
        url = getenv("DISCORD_WEBHOOK_URL_DOWNLOAD")
    elif type_ == "visit":
        content = "Someone just visited the StreamStorm website!"
        url = getenv("DISCORD_WEBHOOK_URL_VISIT")
    else:
        logger.error(f"Unknown type: {type_}. Cannot send discord webhook.")
        return

    data: dict[str, Any] = {
        "embeds": [
            {
                "title": "New Download" if type_ == "download" else "New Visit",
                "description": content + f"\nDate-Time: {get_ist_time()}\nCount: {count}",
                "color": 0x00FF00,
            }
        ]
    }

    try:
        post(url, json=data)
        logger.info(f"Discord webhook sent successfully for {type_} event.")

    except Exception as e:
        logger.error(f"Failed to send Discord webhook: {e}")


__all__: list[str] = ["send_discord_webhook"]
