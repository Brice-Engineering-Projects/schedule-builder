"""Application middleware components."""

from __future__ import annotations

import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from schedule_builder.core.logging import get_logger

logger = get_logger("schedule_builder.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log request and response metadata for each HTTP call."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.exception(
                "Unhandled exception during request %s %s (%.2f ms)",
                request.method,
                request.url.path,
                duration_ms,
            )
            raise

        duration_ms = (time.perf_counter() - start_time) * 1000
        client_host = request.client.host if request.client else "unknown"

        logger.info(
            "%s %s -> %s (%.2f ms) client=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            client_host,
        )
        return response
