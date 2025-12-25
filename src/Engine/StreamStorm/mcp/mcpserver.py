from logging import getLogger, Logger
from typing import Any
from fastmcp import FastMCP
from fastmcp.server.openapi import RouteMap, MCPType
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware
from ..utils.CustomLogger import CustomLogger
from .middlewares.EngineBusyCheck import EngineBusyCheckMiddleware
from .middlewares.CheckStormInProgress import CheckStormInProgressMiddleware
from ..api.fastapi_app import app

# Import resource functions
from .resources import (
    get_storm_channels,
    get_active_channels,
    get_storm_messages,
    get_system_metrics_resource,
    get_system_settings,
    get_available_profiles,
    get_assigned_profiles,
    get_channel_status,
    get_channel_info,
    get_logs
)

CustomLogger().setup_fastmcp_logging()

logger: Logger = getLogger(f"fastmcp.{__name__}")
mcp = FastMCP.from_fastapi(
        app=app,
        # route_maps=[
        #     RouteMap(
        #         methods=["GET"], 
        #         pattern=r".*\{.*\}.*",
        #         mcp_type=MCPType.RESOURCE_TEMPLATE
        #     ),
        #     RouteMap(
        #         methods=["GET"], 
        #         pattern=r".*", 
        #         mcp_type=MCPType.RESOURCE
        #     ),
        # ]
    )

mcp.add_middleware(LoggingMiddleware(
    include_payloads=True,
    max_payload_length=10000,
    logger=logger
))

mcp.add_middleware(RateLimitingMiddleware(
    max_requests_per_second=10.0,
    burst_capacity=20
))

mcp.add_middleware(EngineBusyCheckMiddleware())
mcp.add_middleware(CheckStormInProgressMiddleware())

@mcp.tool(name="greet_streamstorm", tags={"system"})
def greet(name: str) -> str:
    """
    Greet StreamStorm MCP server.
    
    Args:
        name (str): The name of the client.
    
    Returns:
        str: A greeting message.
    """
    return f"Hi {name}, good to have you as a client!"

@mcp.tool(name="get_storm_channels", tags={"storm", "channels"})
def tool_get_storm_channels() -> dict[str, Any]:
    """
    Get all channels with their current status.
    
    Status codes: -1=Idle, 0=Dead, 1=Getting Ready, 2=Ready, 3=Storming.
    Returns channel information including name, logo, and status for all
    channels participating in the current storm session.
    """
    return get_storm_channels()


@mcp.tool(name="get_active_channels", tags={"storm", "channels"})
def tool_get_active_channels() -> dict[str, Any]:
    """
    Get currently active/running channel indices.
    
    Returns a list of channel indices that are currently in Ready (2)
    or Storming (3) state during an active storm session.
    """
    return get_active_channels()


@mcp.tool(name="get_storm_messages", tags={"storm", "messages"})
def tool_get_storm_messages() -> dict[str, Any]:
    """
    Get current message list being sent during the storm.
    
    Returns the list of messages that instances are cycling through
    when sending chat messages to the livestream.
    """
    return get_storm_messages()


@mcp.tool(name="get_system_metrics", tags={"system", "metrics"})
def tool_get_system_metrics() -> dict[str, Any]:
    """
    Get real-time system usage metrics.
    
    Returns CPU percentage, RAM usage (percent and GB), free RAM
    statistics. Useful for monitoring resource consumption during
    storm operations.
    """
    return get_system_metrics_resource()


@mcp.tool(name="get_system_settings", tags={"system", "settings"})
def tool_get_system_settings() -> dict[str, Any]:
    """
    Get current application settings. Mask sensitive data.
    
    Returns configuration including version, environment, host, port,
    operating system, and application data directory path.
    """
    return get_system_settings()


@mcp.tool(name="get_available_profiles", tags={"profiles"})
def tool_get_available_profiles() -> dict[str, Any]:
    """
    Get list of available temporary browser profiles.
    
    Returns profiles created for storm operations. Each profile is
    a browser session that can log into a different YouTube channel.
    """
    return get_available_profiles()


@mcp.tool(name="get_assigned_profiles", tags={"profiles"})
def tool_get_assigned_profiles() -> dict[str, Any]:
    """
    Get profile to channel assignment mapping during storm.
    
    Returns which browser profile is assigned to which channel index
    during an active storm session.
    """
    return get_assigned_profiles()


@mcp.tool(name="get_channel_status", tags={"channel", "status"})
def tool_get_channel_status(channel_id: int) -> dict[str, Any]:
    """
    Get the status of a specific channel.
    
    Args:
        channel_id: The channel index number (0-based).
        
    Status codes: -1=Idle, 0=Dead, 1=Getting Ready, 2=Ready, 3=Storming.
    """
    return get_channel_status(channel_id)


@mcp.tool(name="get_channel_info", tags={"channel", "info"})
def tool_get_channel_info(channel_id: int) -> dict[str, Any]:
    """
    Get full information for a specific channel.
    
    Args:
        channel_id: The channel index number (0-based).
        
    Returns channel name, logo, status, and other metadata.
    """
    return get_channel_info(channel_id)


@mcp.tool(name="get_logs", tags={"logs", "debugging"})
def tool_get_logs(last_n_lines: int) -> dict[str, Any]:
    """
    Get the last N log entries from the current log file.
    
    Args:
        last_n_lines: Number of log lines to retrieve (1-1000).
        
    Returns recent application log entries for debugging and
    monitoring storm operations.
    """
    return get_logs(last_n_lines)


# Do not remove these commented resources
# ============================================================================
# NATIVE MCP RESOURCES
# These are native FastMCP resources (not from FastAPI routes)
# ============================================================================

# Storm Resources
# @mcp.resource("storm://channels")
# def resource_storm_channels() -> dict[str, Any]:
#     """
#     Get all channels with their current status.
    
#     Status codes: -1=Idle, 0=Dead, 1=Getting Ready, 2=Ready, 3=Storming.
#     Returns channel information including name, logo, and status for all
#     channels participating in the current storm session.
#     """
#     return get_storm_channels()


# @mcp.resource("storm://active-channels")
# def resource_active_channels() -> dict[str, Any]:
#     """
#     Get currently active/running channel indices.
    
#     Returns a list of channel indices that are currently in Ready (2)
#     or Storming (3) state during an active storm session.
#     """
#     return get_active_channels()


# @mcp.resource("storm://messages")
# def resource_storm_messages() -> dict[str, Any]:
#     """
#     Get current message list being sent during the storm.
    
#     Returns the list of messages that instances are cycling through
#     when sending chat messages to the livestream.
#     """
#     return get_storm_messages()


# # System Resources
# @mcp.resource("system://metrics")
# def resource_system_metrics() -> dict[str, Any]:
#     """
#     Get real-time system usage metrics.
    
#     Returns CPU percentage, RAM usage (percent and GB), free RAM
#     statistics. Useful for monitoring resource consumption during
#     storm operations.
#     """
#     return get_system_metrics_resource()


# @mcp.resource("system://settings")
# def resource_system_settings() -> dict[str, Any]:
#     """
#     Get current application settings. Mask sensitive data. 
    
#     Returns configuration including version, environment, host, port,
#     operating system, and application data directory path.
#     """
#     return get_system_settings()


# # Profile Resources
# @mcp.resource("profiles://available")
# def resource_available_profiles() -> dict[str, Any]:
#     """
#     Get list of available temporary browser profiles.
    
#     Returns profiles created for storm operations. Each profile is
#     a browser session that can log into a different YouTube channel.
#     """
#     return get_available_profiles()


# @mcp.resource("profiles://assigned")
# def resource_assigned_profiles() -> dict[str, Any]:
#     """
#     Get profile to channel assignment mapping during storm.
    
#     Returns which browser profile is assigned to which channel index
#     during an active storm session.
#     """
#     return get_assigned_profiles()


# # Channel Resource Templates (dynamic URIs)
# @mcp.resource("channel://{channel_id}/status")
# def resource_channel_status(channel_id: int) -> dict[str, Any]:
#     """
#     Get the status of a specific channel.
    
#     Args:
#         channel_id: The channel index number (0-based).
        
#     Status codes: -1=Idle, 0=Dead, 1=Getting Ready, 2=Ready, 3=Storming.
#     """
#     return get_channel_status(channel_id)


# @mcp.resource("channel://{channel_id}/info")
# def resource_channel_info(channel_id: int) -> dict[str, Any]:
#     """
#     Get full information for a specific channel.
    
#     Args:
#         channel_id: The channel index number (0-based).
        
#     Returns channel name, logo, status, and other metadata.
#     """
#     return get_channel_info(channel_id)


# # Logs Resource Template
# @mcp.resource("streamstorm://logs/{last_n_lines}")
# def resource_logs(last_n_lines: int) -> dict[str, Any]:
#     """
#     Get the last N log entries from the current log file.
    
#     Args:
#         last_n_lines: Number of log lines to retrieve (1-1000).
        
#     Returns recent application log entries for debugging and
#     monitoring storm operations.
#     """
#     return get_logs(last_n_lines)

mcp_app = mcp.http_app(path='/')

__all__: list[str] = [
    "mcp_app"
]

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)  