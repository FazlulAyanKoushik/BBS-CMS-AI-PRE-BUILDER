"""Request logging middleware for BBS-CMS AI Pre-Builder.

Logs all HTTP requests with timing information.
"""

from __future__ import annotations

import logging
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests with timing."""

    def __init__(self, app, logger: logging.Logger | None = None):
        super().__init__(app)
        self.logger = logger or logging.getLogger(__name__)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()

        # Log incoming request
        client_ip = request.client.host if request.client else "unknown"
        self.logger.info(
            "📥 %s %s from %s",
            request.method,
            request.url.path,
            client_ip,
        )

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Log response
        status_emoji = "✅" if 200 <= response.status_code < 300 else "❌"
        self.logger.info(
            "📤 %s %s → %d %s (%.2fms)",
            request.method,
            request.url.path,
            response.status_code,
            status_emoji,
            duration_ms,
        )

        return response