from typing import Any, Optional

from ...core.StreamStorm import StreamStorm


def get_channel_status(channel_id: int) -> dict[str, Any]:
    """
    Get the status of a specific channel.
    
    Status codes:
    - -1: Idle
    - 0: Dead
    - 1: Getting Ready
    - 2: Ready
    - 3: Storming
    
    Args:
        channel_id: The channel index number
        
    Returns:
        Dictionary containing:
        - channel_id: The requested channel ID
        - status: Current status code
        - status_text: Human-readable status text
        - found: Whether the channel was found
        - storm_running: Whether a storm is currently active
    """
    status_map = {
        -1: "Idle",
        0: "Dead",
        1: "Getting Ready",
        2: "Ready",
        3: "Storming"
    }
    
    ss_instance: Optional[StreamStorm] = StreamStorm.ss_instance
    
    if ss_instance is None:
        return {
            "channel_id": channel_id,
            "status": None,
            "status_text": "No storm running",
            "found": False,
            "storm_running": False
        }
    
    channel_id_str = str(channel_id)
    
    if channel_id_str not in ss_instance.all_channels:
        return {
            "channel_id": channel_id,
            "status": None,
            "status_text": "Channel not found",
            "found": False,
            "storm_running": True
        }
    
    channel_data = ss_instance.all_channels[channel_id_str]
    status = channel_data.get("status", -1)
    
    return {
        "channel_id": channel_id,
        "status": status,
        "status_text": status_map.get(status, "Unknown"),
        "found": True,
        "storm_running": True
    }


def get_channel_info(channel_id: int) -> dict[str, Any]:
    """
    Get full information for a specific channel.
    
    Args:
        channel_id: The channel index number
        
    Returns:
        Dictionary containing:
        - channel_id: The requested channel ID
        - name: Channel name
        - logo: Channel logo URL/path
        - status: Current status code
        - status_text: Human-readable status text
        - found: Whether the channel was found
        - storm_running: Whether a storm is currently active
    """
    status_map = {
        -1: "Idle",
        0: "Dead",
        1: "Getting Ready",
        2: "Ready",
        3: "Storming"
    }
    
    ss_instance: Optional[StreamStorm] = StreamStorm.ss_instance
    
    if ss_instance is None:
        return {
            "channel_id": channel_id,
            "name": None,
            "logo": None,
            "status": None,
            "status_text": "No storm running",
            "found": False,
            "storm_running": False
        }
    
    channel_id_str = str(channel_id)
    
    if channel_id_str not in ss_instance.all_channels:
        return {
            "channel_id": channel_id,
            "name": None,
            "logo": None,
            "status": None,
            "status_text": "Channel not found",
            "found": False,
            "storm_running": True
        }
    
    channel_data = ss_instance.all_channels[channel_id_str]
    status = channel_data.get("status", -1)
    
    return {
        "channel_id": channel_id,
        "name": channel_data.get("name"),
        "logo": channel_data.get("logo"),
        "status": status,
        "status_text": status_map.get(status, "Unknown"),
        "found": True,
        "storm_running": True
    }


__all__: list[str] = [
    "get_channel_status",
    "get_channel_info"
]
