from typing import Any, Optional
from asyncio import to_thread

from ...core.Profiles import Profiles
from ...core.StreamStorm import StreamStorm


async def get_available_profiles() -> dict[str, Any]:
    """
    Get list of available temporary browser profiles.
    
    Returns:
        Dictionary containing:
        - profiles: List of profile names (e.g., ["temp_profile_1", "temp_profile_2"])
        - count: Total number of available profiles
        - profiles_dir: Directory where profiles are stored
    """
    profiles_instance = Profiles()
    
    try:
        # get_available_temp_profiles may do file system operations
        available_profiles = await to_thread(profiles_instance.get_available_temp_profiles)
    except (FileNotFoundError, ValueError):
        available_profiles = []
    
    return {
        "profiles": available_profiles,
        "count": len(available_profiles),
        "profiles_dir": profiles_instance.profiles_dir
    }


async def get_assigned_profiles() -> dict[str, Any]:
    """
    Get profile to channel assignment mapping during storm.
    
    Returns:
        Dictionary containing:
        - assigned: Mapping of channel index to profile name
        - count: Number of assigned profiles
        - storm_running: Whether a storm is currently active
    """
    ss_instance: Optional[StreamStorm] = StreamStorm.ss_instance
    
    if ss_instance is None:
        return {
            "assigned": {},
            "count": 0,
            "storm_running": False
        }
    
    return {
        "assigned": ss_instance.context.assigned_profiles,
        "count": len(ss_instance.context.assigned_profiles),
        "storm_running": True
    }


__all__: list[str] = [
    "get_available_profiles",
    "get_assigned_profiles"
]
