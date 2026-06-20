"""Core exception types and FastAPI exception handlers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from schedule_builder.core.logging import get_logger

logger = get_logger("schedule_builder.exceptions")


@dataclass
class AppException(Exception):
    """Base application exception with structured error payload metadata."""

    message: str
    status_code: int = 500
    error_code: str = "internal_error"
    details: dict[str, Any] = field(default_factory=dict)


class BadRequestError(AppException):
    def __init__(self, message: str = "Bad request", details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="bad_request",
            details=details or {},
        )


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Unauthorized", details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=401,
            error_code="unauthorized",
            details=details or {},
        )


class ForbiddenError(AppException):
    def __init__(self, message: str = "Forbidden", details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=403,
            error_code="forbidden",
            details=details or {},
        )


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found", details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=404,
            error_code="not_found",
            details=details or {},
        )


class ConflictError(AppException):
    def __init__(self, message: str = "Conflict", details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=409,
            error_code="conflict",
            details=details or {},
        )


class ValidationFailedError(AppException):
    def __init__(self, message: str = "Validation failed", details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="validation_failed",
            details=details or {},
        )


class ServiceUnavailableError(AppException):
    def __init__(
        self,
        message: str = "Service unavailable",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            status_code=503,
            error_code="service_unavailable",
            details=details or {},
        )


def _build_error_response(
    status_code: int, code: str, message: str, details: dict[str, Any]
) -> JSONResponse:
    """Return a consistent error response shape used across handlers."""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
            }
        },
    )


async def app_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Handle first-class app exceptions with stable JSON shape."""
    if not isinstance(exc, AppException):
        return await unhandled_exception_handler(_, exc)

    log_fn = logger.warning if exc.status_code < 500 else logger.error
    log_fn("AppException %s: %s", exc.error_code, exc.message)
    return _build_error_response(
        status_code=exc.status_code,
        code=exc.error_code,
        message=exc.message,
        details=exc.details,
    )


async def http_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Normalize Starlette/FastAPI HTTP exceptions."""
    if not isinstance(exc, StarletteHTTPException):
        return await unhandled_exception_handler(_, exc)

    return _build_error_response(
        status_code=exc.status_code,
        code="http_error",
        message=str(exc.detail),
        details={},
    )


async def validation_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Normalize request validation errors from FastAPI/Pydantic."""
    if not isinstance(exc, RequestValidationError):
        return await unhandled_exception_handler(_, exc)

    return _build_error_response(
        status_code=422,
        code="validation_error",
        message="Request validation failed",
        details={"errors": exc.errors()},
    )


async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler to avoid leaking internal exception details."""
    logger.exception("Unhandled exception: %s", exc)
    return _build_error_response(
        status_code=500,
        code="internal_server_error",
        message="An unexpected error occurred",
        details={},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all application exception handlers to the FastAPI app."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
