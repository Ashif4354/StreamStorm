from logging import getLogger, Logger
from typing import Any
from asyncio import to_thread

from fastmcp import FastMCP
from fastmcp.server.openapi import RouteMap, MCPType
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware

from ..settings import settings
from ..utils.CustomLogger import custom_logger
from .middlewares.EngineBusyCheck import EngineBusyCheckMiddleware
from .middlewares.CheckStormInProgress import CheckStormInProgressMiddleware
from ..api.fastapi_app import app

# Import async resource functions
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

custom_logger.setup_fastmcp_logging()

logger: Logger = getLogger(f"mcpapp.{__name__}")
mcp = FastMCP.from_fastapi(
        app=app,
        route_maps=[
            RouteMap(
                methods=["GET"], 
                pattern=r".*\{.*\}.*",
                mcp_type=MCPType.RESOURCE_TEMPLATE
            ),
            RouteMap(
                methods=["GET"], 
                pattern=r".*", 
                mcp_type=MCPType.RESOURCE
            ),
        ]
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
async def greet(name: str) -> str:
    """
    Greet StreamStorm MCP server.
    
    Args:
        name (str): The name of the client.
    
    Returns:
        str: A greeting message.
    """
    return f"Hi {name}, good to have you as a client!"


@mcp.tool(name="get_storm_channels", tags={"storm", "channels"})
async def tool_get_storm_channels() -> dict[str, Any]:
    """
    Get all channels with their current status.
    
    Status codes: -1=Idle, 0=Dead, 1=Getting Ready, 2=Ready, 3=Storming.
    Returns channel information including name, logo, and status for all
    channels participating in the current storm session.
    """
    return await get_storm_channels()


@mcp.tool(name="get_active_channels", tags={"storm", "channels"})
async def tool_get_active_channels() -> dict[str, Any]:
    """
    Get currently active/running channel indices.
    
    Returns a list of channel indices that are currently in Ready (2)
    or Storming (3) state during an active storm session.
    """
    return await get_active_channels()


@mcp.tool(name="get_storm_messages", tags={"storm", "messages"})
async def tool_get_storm_messages() -> dict[str, Any]:
    """
    Get current message list being sent during the storm.
    
    Returns the list of messages that instances are cycling through
    when sending chat messages to the livestream.
    """
    return await get_storm_messages()


@mcp.tool(name="get_system_metrics", tags={"system", "metrics"})
async def tool_get_system_metrics() -> dict[str, Any]:
    """
    Get real-time system usage metrics.
    
    Returns CPU percentage, RAM usage (percent and GB), free RAM
    statistics. Useful for monitoring resource consumption during
    storm operations.
    """
    return await get_system_metrics_resource()


@mcp.tool(name="get_system_settings", tags={"system", "settings"})
async def tool_get_system_settings() -> dict[str, Any]:
    """
    Get current application settings. Mask sensitive data.
    
    Returns configuration including version, environment, host, port,
    operating system, and application data directory path.
    """
    return await get_system_settings()


@mcp.tool(name="get_available_profiles", tags={"profiles"})
async def tool_get_available_profiles() -> dict[str, Any]:
    """
    Get list of available temporary browser profiles.
    
    Returns profiles created for storm operations. Each profile is
    a browser session that can log into a different YouTube channel.
    """
    return await get_available_profiles()


@mcp.tool(name="get_assigned_profiles", tags={"profiles"})
async def tool_get_assigned_profiles() -> dict[str, Any]:
    """
    Get profile to channel assignment mapping during storm.
    
    Returns which browser profile is assigned to which channel index
    during an active storm session.
    """
    return await get_assigned_profiles()


@mcp.tool(name="get_channel_status", tags={"channel", "status"})
async def tool_get_channel_status(channel_id: int) -> dict[str, Any]:
    """
    Get the status of a specific channel.
    
    Args:
        channel_id: The channel index number (0-based).
        
    Status codes: -1=Idle, 0=Dead, 1=Getting Ready, 2=Ready, 3=Storming.
    """
    return await get_channel_status(channel_id)


@mcp.tool(name="get_channel_info", tags={"channel", "info"})
async def tool_get_channel_info(channel_id: int) -> dict[str, Any]:
    """
    Get full information for a specific channel.
    
    Args:
        channel_id: The channel index number (0-based).
        
    Returns channel name, logo, status, and other metadata.
    """
    return await get_channel_info(channel_id)


@mcp.tool(name="get_logs", tags={"logs", "debugging"})
async def tool_get_logs(last_n_lines: int) -> dict[str, Any]:
    """
    Get the last N log entries from the current log file.
    
    Args:
        last_n_lines: Number of log lines to retrieve (1-1000).
        
    Returns recent application log entries for debugging and
    monitoring storm operations.
    """
    return await get_logs(last_n_lines)


# ============================================================================
# ADDITIONAL TOOLS (wrapping FastAPI endpoints as tools)
# ============================================================================

@mcp.tool(name="get_storm_status", tags={"storm", "status"})
async def tool_get_storm_status() -> dict[str, Any]:
    """
    Get the current storm status.
    
    Returns whether a storm is currently running or not.
    Useful for checking if the engine is busy before starting new operations.
    
    Returns:
        success (bool): True if the request was successful
        storm (bool): True if a storm is currently running
        message (str): Human-readable status message
    """
    from ..core.StreamStorm import StreamStorm
    
    if StreamStorm.ss_instance is None:
        return {
            "success": True,
            "storm": False,
            "message": "Storm is not running",
        }
    else:
        return {
            "success": True,
            "storm": True,
            "message": "Storm is running",
        }


@mcp.tool(name="get_message_stats", tags={"storm", "messages", "stats"})
async def tool_get_message_stats() -> dict[str, Any]:
    """
    Get real-time message statistics for the current storm.
    
    Returns the total number of messages sent and the current message rate
    (messages per minute) during an active storm session.
    
    Returns:
        success (bool): True if the request was successful
        message_count (int): Total number of messages sent during this storm
        message_rate (float): Current message rate in messages per minute
        message (str): Status message
    """
    from ..core.StreamStorm import StreamStorm
    
    if StreamStorm.ss_instance is None:
        return {
            "success": False,
            "message_count": 0,
            "message_rate": 0.0,
            "message": "No storm is running"
        }
    
    async with StreamStorm.ss_instance.message_counter_lock:
        message_count = StreamStorm.ss_instance.context.message_count
    
    return {
        "success": True,
        "message_count": message_count,
        "message_rate": StreamStorm.ss_instance.context.message_rate,
        "message": "Message statistics fetched successfully"
    }


@mcp.tool(name="get_storm_context", tags={"storm", "context"})
async def tool_get_storm_context() -> dict[str, Any]:
    """
    Get the current storm context and statistics.
    
    Returns detailed information about the running storm including:
    1. All configured storm data received via form
    2. Status of each channel - Idle(-1), Dead(0), Getting Ready(1), Ready(2), Storming(3)
    3. Storm Status - Running, Stopped, Paused
    4. Storm Start Time
    
    Returns:
        success (bool): True if the request was successful
        context (dict): Current storm context with runtime statistics
        message (str): Confirmation message
    """
    from ..core.StreamStorm import StreamStorm
    
    if StreamStorm.ss_instance is None:
        return {
            "success": False,
            "context": None,
            "message": "No storm is running"
        }
    
    return {
        "success": True,
        "context": StreamStorm.ss_instance.context.model_dump(),
        "message": "Context fetched successfully"
    }


@mcp.tool(name="get_ai_provider_keys", tags={"settings", "ai"})
async def tool_get_ai_provider_keys() -> dict[str, Any]:
    """
    Get all AI provider configurations and keys.
    
    Returns the complete AI settings including API keys (redacted),
    models, base URLs, and default provider configuration.
    
    Returns:
        success (bool): True if the request was successful
        providers (dict): Configuration for each AI provider (openai, anthropic, google)
        defaultProvider (str): Currently selected default provider
        defaultModel (str): Currently selected default model
        defaultBaseUrl (str): Base URL for the default provider
    """
    from ..settings import settings

    settings_copy = settings.model_copy()
    settings_copy.ai.providers.openai.apiKey = "<REDACTED>"
    settings_copy.ai.providers.anthropic.apiKey = "<REDACTED>"
    settings_copy.ai.providers.google.apiKey = "<REDACTED>"
    
    try:
        return {"success": True, **settings_copy.ai.model_dump()}
    except Exception as e:
        return {"success": False, "message": f"Error fetching AI keys: {str(e)}"}


@mcp.tool(name="get_settings", tags={"settings", "system", "config"})
async def tool_get_settings() -> dict[str, Any]:
    """
    Get all application settings including engine config and default AI provider.
    
    Returns engine configuration (version, log file path) and 
    default AI provider settings under the 'ai' sub-key.
    
    Returns:
        success (bool): True if the request was successful
        version (str): StreamStorm engine version
        log_file_path (str): Path to the StreamStorm engine log file
        ai (dict): Default AI provider settings
            - defaultProvider (str): Currently selected default provider
            - defaultModel (str): Currently selected model for the default provider
            - defaultBaseUrl (str): Base URL for the default provider API
    """
    from ..settings import settings
    
    try:
        return {
            "success": True,
            "version": settings.version,
            "log_file_path": settings.log_file_path,
            "ai": {
                "defaultProvider": settings.ai.defaultProvider,
                "defaultModel": settings.ai.defaultModel,
                "defaultBaseUrl": settings.ai.defaultBaseUrl,
            },
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error fetching settings: {str(e)}",
        }


@mcp.tool(name="health_check", tags={"system"})
async def tool_health_check() -> dict[str, Any]:
    """
    Check if StreamStorm engine is running.
    
    Simple health check endpoint to verify the engine is operational.
    
    Returns:
        success (bool): True if the engine is running
        message (str): Confirmation message
    """
    return {"success": True, "message": "I am the StreamStorm Engine"}


@mcp.tool(name="get_system_ram_info", tags={"system", "metrics"})
async def tool_get_system_ram_info() -> dict[str, Any]:
    """
    Get system RAM information.
    
    Returns the current free and total RAM on the system.
    Note: This tool is deprecated and may be removed in future versions.
    Use get_system_metrics for more comprehensive system information.
    
    Returns:
        free (float): Available RAM in gigabytes
        total (float): Total RAM in gigabytes
    """
    from psutil import virtual_memory
    
    def get_ram_info() -> dict[str, float]:
        mem = virtual_memory()
        return {
            "free": mem.available / (1024**3),
            "total": mem.total / (1024**3),
        }
    
    return await to_thread(get_ram_info)



@mcp.tool(name="get_storm_history", tags={"storm", "history"})
async def tool_get_storm_history(last_n_requests: int = 2) -> dict[str, Any]:
    """
    Get the last N storm requests from the history log.
    
    Retrieves historical storm request data including video URL, chat URL,
    messages, channels used, and other configuration from past storms.
    
    Args:
        last_n_requests: Number of storm requests to retrieve (default: 2, max: 20).
        
    Returns:
        success (bool): True if the request was successful
        requests (list): List of storm request entries
        count (int): Number of requests returned
        message (str): Status message
    """
    from aiofiles import open as aio_open
    
    # Clamp to reasonable limits
    n_requests = max(1, min(last_n_requests, 20))
    
    history_file = settings.app_data_dir / "logs" / "History.log"
    
    if not history_file.exists():
        return {
            "success": False,
            "requests": [],
            "count": 0,
            "message": "No history yet"
        }
    
    try:
        async with aio_open(history_file, "r", encoding="utf-8") as f:
            content = await f.read()
        
        # Split by the separator (60 equal signs followed by newline)
        separator = "=" * 60 + "\n"
        entries = content.split(separator)
        
        # Filter out empty entries and get the last N
        entries = [e.strip() for e in entries if e.strip()]
        last_entries = entries[-n_requests:] if len(entries) >= n_requests else entries
        
        # Reverse to show most recent first
        last_entries.reverse()
        
        return {
            "success": True,
            "requests": last_entries,
            "count": len(last_entries),
            "message": f"Retrieved {len(last_entries)} storm request(s)"
        }
        
    except Exception as e:
        return {
            "success": False,
            "requests": [],
            "count": 0,
            "message": f"Error reading history: {str(e)}"
        }


# ============================================================================
# NATIVE MCP RESOURCES
# These are native FastMCP resources (not from FastAPI routes)
# ============================================================================

# Storm Resources
@mcp.resource("storm://channels")
async def resource_storm_channels() -> dict[str, Any]:
    """
    Get all channels with their current status.
    
    Status codes: -1=Idle, 0=Dead, 1=Getting Ready, 2=Ready, 3=Storming.
    Returns channel information including name, logo, and status for all
    channels participating in the current storm session.
    """
    return await get_storm_channels()


@mcp.resource("storm://active-channels")
async def resource_active_channels() -> dict[str, Any]:
    """
    Get currently active/running channel indices.
    
    Returns a list of channel indices that are currently in Ready (2)
    or Storming (3) state during an active storm session.
    """
    return await get_active_channels()


@mcp.resource("storm://messages")
async def resource_storm_messages() -> dict[str, Any]:
    """
    Get current message list being sent during the storm.
    
    Returns the list of messages that instances are cycling through
    when sending chat messages to the livestream.
    """
    return await get_storm_messages()


@mcp.resource("storm://message-stats")
async def resource_message_stats() -> dict[str, Any]:
    """
    Get real-time message statistics for the current storm.
    
    Returns the total number of messages sent and the current message rate
    (messages per minute) during an active storm session.
    """
    from ..core.StreamStorm import StreamStorm
    
    if StreamStorm.ss_instance is None:
        return {
            "success": False,
            "message_count": 0,
            "message_rate": 0.0,
            "message": "No storm is running"
        }
    
    async with StreamStorm.ss_instance.message_counter_lock:
        message_count = StreamStorm.ss_instance.context.message_count
    
    return {
        "success": True,
        "message_count": message_count,
        "message_rate": StreamStorm.ss_instance.context.message_rate,
        "message": "Message statistics fetched successfully"
    }


# System Resources
@mcp.resource("system://metrics")
async def resource_system_metrics() -> dict[str, Any]:
    """
    Get real-time system usage metrics.
    
    Returns CPU percentage, RAM usage (percent and GB), free RAM
    statistics. Useful for monitoring resource consumption during
    storm operations.
    """
    return await get_system_metrics_resource()


@mcp.resource("system://settings")
async def resource_system_settings() -> dict[str, Any]:
    """
    Get current application settings. Mask sensitive data. 
    
    Returns configuration including version, environment, host, port,
    operating system, and application data directory path.
    """
    return await get_system_settings()


# Profile Resources
@mcp.resource("profiles://available")
async def resource_available_profiles() -> dict[str, Any]:
    """
    Get list of available temporary browser profiles.
    
    Returns profiles created for storm operations. Each profile is
    a browser session that can log into a different YouTube channel.
    """
    return await get_available_profiles()


@mcp.resource("profiles://assigned")
async def resource_assigned_profiles() -> dict[str, Any]:
    """
    Get profile to channel assignment mapping during storm.
    
    Returns which browser profile is assigned to which channel index
    during an active storm session.
    """
    return await get_assigned_profiles()


# Channel Resource Templates (dynamic URIs)
@mcp.resource("channel://{channel_id}/status")
async def resource_channel_status(channel_id: int) -> dict[str, Any]:
    """
    Get the status of a specific channel.
    
    Args:
        channel_id: The channel index number (0-based).
        
    Status codes: -1=Idle, 0=Dead, 1=Getting Ready, 2=Ready, 3=Storming.
    """
    return await get_channel_status(channel_id)


@mcp.resource("channel://{channel_id}/info")
async def resource_channel_info(channel_id: int) -> dict[str, Any]:
    """
    Get full information for a specific channel.
    
    Args:
        channel_id: The channel index number (0-based).
        
    Returns channel name, logo, status, and other metadata.
    """
    return await get_channel_info(channel_id)


# Logs Resource Template
@mcp.resource("streamstorm://logs/{last_n_lines}")
async def resource_logs(last_n_lines: int) -> dict[str, Any]:
    """
    Get the last N log entries from the current log file.
    
    Args:
        last_n_lines: Number of log lines to retrieve (1-1000).
        
    Returns recent application log entries for debugging and
    monitoring storm operations.
    """
    return await get_logs(last_n_lines)

mcp_app = mcp.http_app(path='/mcp')

__all__: list[str] = [
    "mcp_app"
]

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)  