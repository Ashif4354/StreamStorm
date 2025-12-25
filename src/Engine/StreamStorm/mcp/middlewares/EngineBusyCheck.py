from os import environ

from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import ToolError

from ...settings import settings

class EngineBusyCheckMiddleware(Middleware):

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        tool_name: str = context.message.name
        
        if tool_name.lower() in settings.busy_tools and environ.get("BUSY") == "1":
            raise ToolError(f"Engine is busy: {environ.get('BUSY_REASON')}")

        return await call_next(context)


__all__: list[str] = ["EngineBusyCheckMiddleware"]
