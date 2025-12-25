from logging import getLogger, Logger
from fastmcp import FastMCP
from fastmcp.server.openapi import RouteMap, MCPType
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware
from ..utils.CustomLogger import CustomLogger
from .middlewares.EngineBusyCheck import EngineBusyCheckMiddleware
from .middlewares.CheckStormInProgress import CheckStormInProgressMiddleware
from ..api.fastapi_app import app

CustomLogger().setup_fastmcp_logging()

logger: Logger = getLogger(f"fastmcp.{__name__}")
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

@mcp.tool
def greet(name: str) -> str:
    """
    Greet StreamStorm MCP server.
    
    Args:
        name (str): The name of the client.
    
    Returns:
        str: A greeting message.
    """
    return f"Hi {name}, good to have you as a client!"

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)  