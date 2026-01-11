from typing import Any, Optional
from contextlib import suppress
from logging import getLogger, Logger

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

def get_cookies() -> Optional[list]:
    from json import load, JSONDecodeError
    
    cookies: Optional[list] = None

    with suppress(FileNotFoundError, JSONDecodeError):
        with open(settings.cookies_path, "r", encoding="utf-8") as file:
            cookies = load(file)

    if cookies is None:
        logger.warning("No cookies found, Redirecting to login page...")
        return cookies

    try:
        cookies = Cookies(cookies=cookies).model_dump()["cookies"]
        logger.info("Valid cookies found, Logging in with cookies now.")

    except (ValueError, TypeError) as e:
        logger.error(f"Error parsing cookies: {e}")
        logger.warning("Invalid cookies found, Redirecting to login page...")
        cookies = None
    
    return cookies
    

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


__all__ = ["parse_netscape_cookies", "get_cookies"]
