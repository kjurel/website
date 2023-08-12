import typing as t

from asgi_correlation_id import correlation_id
from fastapi.exception_handlers import http_exception_handler
from fastapi.requests import HTTPException, Request
from starlette.responses import JSONResponse


class APIException(Exception):
    def __init__(
        self,
        error_code: int = 000,
        status_code: int = 500,
        detail="",
        message="",
        *args,
        **kwargs,
    ):
        Exception.__init__(self, *args, **kwargs)

        self.error_code = error_code
        self.message = message
        self.detail = detail
        self.status_code = status_code

    def __str__(self):
        return f"APIException(status_code={self.status_code}, detail={self.message})"


async def on_api_exception(request: Request, exception: APIException) -> JSONResponse:
    content: t.Dict[str, t.Dict[str, t.Any]] = {
        "error": {"error_code": exception.error_code}
    }

    if exception.message:
        content["error"]["message"] = exception.message

    if exception.detail:
        content["error"]["detail"] = exception.detail

    return JSONResponse(content=content, status_code=exception.status_code)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return await http_exception_handler(
        request,
        HTTPException(
            500,
            "Internal server error",
            headers={"X-Request-ID": correlation_id.get() or ""},
        ),
    )
