from logging import Logger, getLogger
from os import environ

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from ...core.StreamStorm import StreamStorm
from ...settings import settings

logger: Logger = getLogger(f"fastapi.{__name__}")


class LogRequestMiddleware(BaseHTTPMiddleware):
    __slots__: tuple[str, ...] = ()

    async def dispatch(self, request: Request, call_next) -> Response:
        path: str = request.url.path

        client_ip: str = request.client.host if request.client else "unknown"
        url: str = str(request.url)
        method: str = request.method
        headers: dict = dict(request.headers)

        try:
            body: bytes = await request.body()
            body_str: str = body.decode("utf-8", errors="replace")

        except Exception:
            body_str: str = "<unable to decode>"

        finally:
            if path in settings.sensitive_endpoints and method == "POST":                
                final_body: str = "  <hidden-due-to-sensitive-data>\n"
            else:
                final_body: str = f"{body_str if body_str.strip() else '  <empty>'}\n"
                


        logger.debug(
            "[REQUEST RECEIVED]\n"
            f"IP: {client_ip}\n"
            f"URL: {url}\n"
            f"Path: {path}\n"
            f"Method: {method}\n"
            "Headers:\n" + "\n".join([f"  {k}: {v}" for k, v in headers.items()]) + "\n"
            "Body:\n" + final_body
        )

        response: Response = await call_next(request)

        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    __slots__: tuple[str, ...] = ()

    async def dispatch(self, request: Request, call_next) -> Response:
        path: str = request.url.path
        method: str = request.method

        if method == "POST":
            if path in settings.busy_endpoints:
                if environ.get("BUSY") == "1":
                    return JSONResponse(
                        status_code=429,  # Too Many Requests
                        content={
                            "success": False,
                            "message": f"Engine is Busy: {environ.get('BUSY_REASON')}",
                        },
                        headers=settings.cors_headers,
                    )

            elif path in settings.storm_controls_endpoints:
                if StreamStorm.ss_instance is None:
                    return JSONResponse(
                        status_code=409,  # Conflict
                        content={
                            "success": False,
                            "message": "No storm is running. Start a storm first.",
                        },
                        headers=settings.cors_headers,
                    )

                    # return JSONResponse(
                    #     status_code=200,
                    #     content={
                    #         "success": True,
                    #         "message": "Testing",
                    #     },
                    # )

        if (method == "GET" and path in settings.storm_controls_endpoints and 
        StreamStorm.ss_instance is None):
            return JSONResponse(
                status_code=409,  # Conflict
                content={
                    "success": False,
                    "message": "No storm is running. Start a storm first.",
                },
                headers=settings.cors_headers,
            )

        response: JSONResponse = await call_next(request)

        return response


__all__: list[str] = ["LogRequestMiddleware", "RequestValidationMiddleware"]
