from fastapi import Request
from logging import Logger, getLogger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from os import environ
from fastapi.responses import JSONResponse

from ...core.StreamStorm import StreamStorm

logger: Logger = getLogger(f"fastapi.{__name__}")

polling_paths: set[str] = {"/config", "/get_ram_info"}


class LogRequestMiddleware(BaseHTTPMiddleware):
    __slots__: tuple[str, ...] = ()

    async def dispatch(self, request: Request, call_next) -> Response:
        path: str = request.url.path

        if path not in polling_paths:
            client_ip: str = request.client.host if request.client else "unknown"
            url: str = str(request.url)
            method: str = request.method
            headers: dict = dict(request.headers)

            try:
                body: bytes = await request.body()
                body_str: str = body.decode("utf-8", errors="replace")

            except Exception:
                body_str: str = "<unable to decode>"

            logger.debug(
                "[REQUEST RECEIVED]\n"
                f"IP: {client_ip}\n"
                f"URL: {url}\n"
                f"Path: {path}\n"
                f"Method: {method}\n"
                "Headers:\n"
                + "\n".join([f"  {k}: {v}" for k, v in headers.items()])
                + "\n"
                "Body:\n"
                f"{body_str if body_str.strip() else '  <empty>'}\n"
            )

        response: Response = await call_next(request)

        return response


storm_controls_endpoints: set[str] = {
    "/storm/pause",
    "/storm/resume",
    "/storm/change_messages",
    "/storm/start_storm_dont_wait",
    "/storm/change_slow_mode",
    "/storm/start_more_channels",
    # "/storm/kill_instance"
}


class RequestValidationMiddleware(BaseHTTPMiddleware):
    __slots__: tuple[str, ...] = ()

    async def dispatch(self, request: Request, call_next) -> Response:
        path: str = request.url.path
        method: str = request.method

        cors_headers: dict[str, str] = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }

        if method == "POST":
            if path in (
                "/storm/start",
                "/environment/profiles/create",
                "/environment/profiles/delete",
            ):
                if environ.get("BUSY") == "1":
                    return JSONResponse(
                        status_code=429,
                        content={
                            "success": False,
                            "message": f"Engine is Busy: {environ.get('BUSY_REASON')}",
                        },
                        headers=cors_headers,
                    )

            elif path in storm_controls_endpoints:
                if StreamStorm.ss_instance is None:
                    return JSONResponse(
                        status_code=409,
                        content={
                            "success": False,
                            "message": "No storm is running. Start a storm first.",
                        },
                        headers=cors_headers,
                    )
                    
                    # return JSONResponse(
                    #     status_code=200,
                    #     content={
                    #         "success": True,
                    #         "message": "Testing",
                    #     },                  
                    # )

        if (
            method == "GET"
            and path in storm_controls_endpoints
            and StreamStorm.ss_instance is None
        ):
            return JSONResponse(
                status_code=409,
                content={
                    "success": False,
                    "message": "No storm is running. Start a storm first.",
                },
                headers=cors_headers,
            )

        response: JSONResponse = await call_next(request)

        return response


__all__: list[str] = ["LogRequestMiddleware", "RequestValidationMiddleware"]
