"""
MCP Resources for StreamStorm.

This module exports all resource functions that can be registered with the MCP server.
"""

from .storm import (
    get_storm_channels,
    get_active_channels,
    get_storm_messages
)
from .system import (
    get_system_metrics_resource,
    get_system_settings
)
from .profiles import (
    get_available_profiles,
    get_assigned_profiles
)
from .channel import (
    get_channel_status,
    get_channel_info
)
from .logs import get_logs


__all__: list[str] = [
    # Storm resources
    "get_storm_channels",
    "get_active_channels",
    "get_storm_messages",
    # System resources
    "get_system_metrics_resource",
    "get_system_settings",
    # Profile resources
    "get_available_profiles",
    "get_assigned_profiles",
    # Channel resource templates
    "get_channel_status",
    "get_channel_info",
    # Logs resource template
    "get_logs"
]
