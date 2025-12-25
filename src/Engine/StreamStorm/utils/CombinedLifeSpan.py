from contextlib import asynccontextmanager

from fastapi import FastAPI

from ..api.lib.LifeSpan import lifespan as fastapi_lifespan
from ..mcp.mcpserver import mcp_app
from ..api.fastapi_app import app as fastapi_app

@asynccontextmanager
async def combined_lifespan(app: FastAPI) -> None:
    
    async with fastapi_lifespan(fastapi_app):
        async with mcp_app.lifespan(app):
            yield


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