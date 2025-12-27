from contextlib import asynccontextmanager
from logging import getLogger, Logger

from fastapi import FastAPI

from ..api.lib.LifeSpan import lifespan as fastapi_lifespan
from ..mcp.mcpserver import mcp_app
from ..api.fastapi_app import app as fastapi_app

logger: Logger = getLogger(__name__)

@asynccontextmanager
async def combined_lifespan(app: FastAPI) -> None:
    logger.debug("Starting combined lifespan of API and MCP server")
        
    async with fastapi_lifespan(fastapi_app):
        async with mcp_app.lifespan(app):
            yield
            
    logger.debug("Combined lifespan of API and MCP server ended")


# @asynccontextmanager
# async def combined_lifespan(app: FastAPI):
#     async with AsyncExitStack() as stack:
#         # 1. Trigger the mcp_app lifespan
#         # Assuming mcp_app.lifespan is an async context manager
#         await stack.enter_async_context(mcp_app.lifespan(app))
        
#         # 2. Trigger the original fastapi_app lifespan
#         # Note: We pass fastapi_app to its own lifespan context
#         await stack.enter_async_context(fastapi_app.router.lifespan_context(fastapi_app))
        
#         # Yield control back to the application (Startup done)
#         yield

__all__ = ["combined_lifespan"]