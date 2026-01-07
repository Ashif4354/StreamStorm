from typing import Any


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
            "path": path,
            "secure": secure.upper() == "TRUE",
            "httpOnly": False,
            "sameSite": "Lax",
        })
    
    return cookies


__all__ = ["parse_netscape_cookies"]
