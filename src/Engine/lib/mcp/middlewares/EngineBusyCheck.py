from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import ToolError

from ...settings import settings
from ...core.EngineContext import EngineContext

class EngineBusyCheckMiddleware(Middleware):

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        tool_name: str = context.message.name
        
        if tool_name.lower() in settings.busy_tools and EngineContext.is_busy():
            raise ToolError(f"Engine is busy: {EngineContext.get_busy_reason()}")

        return await call_next(context)


__all__: list[str] = ["EngineBusyCheckMiddleware"]

