from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import ToolError

from ...settings import settings
from ...core.StreamStorm import StreamStorm

class CheckStormInProgressMiddleware(Middleware):

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        tool_name: str = context.message.name
        
        if tool_name.lower() in settings.storm_control_tools and StreamStorm.ss_instance is None:
            raise ToolError("No storm is running. Start a storm first.")

        return await call_next(context)

__all__: list[str] = ["CheckStormInProgressMiddleware"]