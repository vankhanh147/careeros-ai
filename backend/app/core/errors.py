import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("careeros_api.errors")


class AppError(HTTPException):
    def __init__(self, status_code: int, detail: str, code: str, headers: dict[str, str] | None = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.code = code


def raise_app_error(status_code: int, detail: str, code: str, headers: dict[str, str] | None = None) -> None:
    raise AppError(status_code=status_code, detail=detail, code=code, headers=headers)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return _error_response(exc.status_code, str(exc.detail), exc.code, headers=exc.headers)

    @app.exception_handler(HTTPException)
    async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else "Request could not be processed"
        return _error_response(exc.status_code, detail, _default_code(exc.status_code), headers=exc.headers)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.info("Request validation failed", extra={"path": request.url.path})
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            _format_validation_error(exc.errors()),
            "VALIDATION_ERROR",
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled backend error", extra={"path": request.url.path})
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Internal server error",
            "INTERNAL_SERVER_ERROR",
        )


def _error_response(status_code: int, detail: str, code: str, headers: dict[str, str] | None = None) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail, "code": code}, headers=headers)


def _default_code(status_code: int) -> str:
    return {
        status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
        status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
        status.HTTP_403_FORBIDDEN: "FORBIDDEN",
        status.HTTP_404_NOT_FOUND: "NOT_FOUND",
        status.HTTP_409_CONFLICT: "CONFLICT",
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: "FILE_TOO_LARGE",
        status.HTTP_422_UNPROCESSABLE_ENTITY: "VALIDATION_ERROR",
    }.get(status_code, "HTTP_ERROR")


def _format_validation_error(errors: list[dict[str, Any]]) -> str:
    if not errors:
        return "Invalid request data"
    first_error = errors[0]
    location = ".".join(str(part) for part in first_error.get("loc", []) if part != "body")
    message = str(first_error.get("msg", "Invalid value"))
    if location:
        return f"Invalid field '{location}': {message}"
    return message