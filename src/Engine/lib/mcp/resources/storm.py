from typing import Any, Optional

from ...core.StreamStorm import StreamStorm


async def get_storm_channels() -> dict[str, Any]:
    """
    Get all channels with their current status.
    
    Status codes:
    - -1: Idle
    - 0: Dead
    - 1: Getting Ready
    - 2: Ready
    - 3: Storming
    
    Returns:
        Dictionary containing all channels and their status information.
        Returns empty dict if no storm is running.
    """
    ss_instance: Optional[StreamStorm] = StreamStorm.ss_instance
    
    if ss_instance is None:
        return {
            "channels": {},
            "total_channels": 0,
            "storm_running": False
        }
    
    return {
        "channels": ss_instance.context.all_channels,
        "total_channels": ss_instance.context.total_channels,
        "storm_running": True
    }


async def get_active_channels() -> dict[str, Any]:
    """
    Get currently active/running channel indices.
    
    Returns:
        Dictionary containing list of active channel indices.
        Returns empty list if no storm is running.
    """
    ss_instance: Optional[StreamStorm] = StreamStorm.ss_instance
    
    if ss_instance is None:
        return {
            "active_channels": [],
            "count": 0,
            "storm_running": False
        }
    
    # Active channels are those with status 2 (Ready) or 3 (Storming)
    active: list[int] = []
    for index_str, channel_data in ss_instance.context.all_channels.items():
        status = channel_data.get("status", -1)
        if status in (2, 3):  # Ready or Storming
            active.append(int(index_str))
    
    return {
        "active_channels": active,
        "count": len(active),
        "storm_running": True
    }


async def get_storm_messages() -> dict[str, Any]:
    """
    Get current message list being sent during the storm.
    
    Returns:
        Dictionary containing the messages list and count.
        Returns empty list if no storm is running.
    """
    ss_instance: Optional[StreamStorm] = StreamStorm.ss_instance
    
    if ss_instance is None:
        return {
            "messages": [],
            "count": 0,
            "storm_running": False
        }
    
    return {
        "messages": ss_instance.context.messages,
        "count": len(ss_instance.context.messages),
        "storm_running": True
    }


__all__: list[str] = [
    "get_storm_channels",
    "get_active_channels",
    "get_storm_messages"
]
