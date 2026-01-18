from typing import Any, Optional
from contextlib import suppress
from logging import getLogger, Logger
from time import time

from pydantic import BaseModel

from ..settings import settings

logger: Logger = getLogger(f"streamstorm.{__name__}")

class Cookie(BaseModel):
    domain: str 
    name: str
    value: str
    path: str
    secure: bool
    httpOnly: bool
    sameSite: str
    expiry: Optional[int] = None

class Cookies(BaseModel):
    cookies: list[Cookie]


def is_expired(cookie: dict[str, Any]) -> bool:
    expiry: float = cookie.get("expiry", 0)

    if not expiry:
        return False

    return expiry < time()


def get_cookies() -> Optional[list]:
    from json import load, JSONDecodeError
    
    cookies_data: Optional[list] = None

    with suppress(FileNotFoundError, JSONDecodeError):
        with open(settings.cookies_path, "r", encoding="utf-8") as file:
            cookies_data = load(file)

    if cookies_data is None:
        logger.warning("No cookies found.")
        return None

    try:
        validated_cookies = Cookies(cookies=cookies_data).model_dump()["cookies"]
        logger.info("Valid cookies found, Logging in with cookies now.")

    except (ValueError, TypeError) as e:
        logger.error(f"Error parsing cookies: {e}")
        logger.warning("Invalid cookies found.")
        return None

    final_cookies: list = []

    for cookie in validated_cookies:
        if is_expired(cookie):
            logger.warning("Expired cookie found: %s", cookie.get("name"))
            continue
        
        final_cookies.append(cookie)
    
    if not final_cookies:
        logger.error("One or more cookies are expired, Login again or Provide valid cookies.")
        raise SystemError("One or more cookies are expired, Login again or Provide valid cookies.")
    
    return final_cookies
    

def parse_netscape_cookies(file_content: str, filename: str) -> list[dict[str, Any]]:
    """
    Parse Netscape format cookies from file content.
    
    Args:
        file_content: The raw text content of the Netscape cookie file
        filename: The name of the file (for error messages)
    
    Returns:
        List of cookie dictionaries with domain, name, value, path, secure, httpOnly, sameSite
    
    Raises:
        ValueError: If a cookie line is malformed
    """
    cookies: list[dict[str, Any]] = []
    
    for line in file_content.strip().split('\n'):
        line = line.strip()
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
        
        parts = line.split('\t')
        if len(parts) < 7:
            # Try space-separated format
            parts = line.split()
            if len(parts) < 7:
                raise ValueError(f"Invalid Netscape cookie line in {filename}: {line[:50]}...")
        
        domain, include_subdomains, path, secure, expires, name, value = parts[:7]
        
        cookies.append({
            "domain": domain,
            "name": name,
            "value": value,
            "expiry": int(expires),
            "path": path,
            "secure": secure.upper() == "TRUE",
            "httpOnly": False,
            "sameSite": "Lax",
        })
    
    return cookies


__all__ = ["parse_netscape_cookies", "get_cookies", "is_expired"]
