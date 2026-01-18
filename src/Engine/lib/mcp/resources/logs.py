from typing import Any
from collections import deque

from aiofiles import open as aio_open

from ...settings import settings


async def get_logs(last_n_lines: int = 50) -> dict[str, Any]:
    """
    Get the last N log entries from the current session log file.
    
    Args:
        last_n_lines: Number of log lines to retrieve (default: 50)
        
    Returns:
        Dictionary containing:
        - logs: List of log entries (most recent last)
        - count: Number of entries returned
        - log_file: Path to the current log file
        - success: Whether logs were retrieved successfully
        - error: Error message if any
    """
    if last_n_lines < 1:
        last_n_lines = 1
    elif last_n_lines > 1000:
        last_n_lines = 1000  # Cap to prevent excessive memory usage
    
    log_file_path = settings.log_file_path
    
    if not log_file_path:
        return {
            "logs": [],
            "count": 0,
            "log_file": None,
            "success": False,
            "error": "No log file path set for this session"
        }
    
    try:
        async with aio_open(log_file_path, "r", encoding="utf-8") as f:
            all_lines = await f.readlines()
            
        # Get last N lines
        last_lines = all_lines[-last_n_lines:] if len(all_lines) > last_n_lines else all_lines
        
        # Strip newlines and filter empty lines
        log_entries = [line.strip() for line in last_lines if line.strip()]
        
        return {
            "logs": log_entries,
            "count": len(log_entries),
            "log_file": log_file_path,
            "success": True,
            "error": None
        }
        
    except (IOError, OSError, FileNotFoundError) as e:
        return {
            "logs": [],
            "count": 0,
            "log_file": log_file_path,
            "success": False,
            "error": f"Failed to read log file: {str(e)}"
        }


__all__: list[str] = ["get_logs"]
