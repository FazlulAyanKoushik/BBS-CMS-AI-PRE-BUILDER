"""Rate limiting middleware for BBS-CMS AI Pre-Builder.

Provides configurable rate limiting with support for:
- Per-IP rate limiting
- Per-endpoint rate limiting
- Configurable limits via settings
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import settings


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10  # Allow short bursts


@dataclass
class ClientState:
    """Tracks request state for a client."""
    minute_requests: list[float] = field(default_factory=list)
    hour_requests: list[float] = field(default_factory=list)
    burst_requests: list[float] = field(default_factory=list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with sliding window algorithm."""

    def __init__(
        self,
        app,
        config: Optional[RateLimitConfig] = None,
        exempt_paths: Optional[list[str]] = None,
    ):
        super().__init__(app)
        self.config = config or RateLimitConfig(
            requests_per_minute=settings.rate_limit_per_minute if hasattr(settings, 'rate_limit_per_minute') else 60,
            requests_per_hour=settings.rate_limit_per_hour if hasattr(settings, 'rate_limit_per_hour') else 1000,
            burst_limit=settings.rate_limit_burst if hasattr(settings, 'rate_limit_burst') else 10,
        )
        self.exempt_paths = exempt_paths or ["/api/health", "/docs", "/openapi.json", "/redoc"]
        self.clients: dict[str, ClientState] = defaultdict(ClientState)

    def _get_client_key(self, request: Request) -> str:
        """Generate client identifier from request."""
        # Use X-Forwarded-For if behind proxy, otherwise client host
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        return f"{ip}:{request.url.path}"

    def _is_exempt(self, path: str) -> bool:
        """Check if path is exempt from rate limiting."""
        for exempt in self.exempt_paths:
            if path.startswith(exempt):
                return True
        return False

    def _clean_old_requests(self, requests: list[float], window_seconds: float) -> list[float]:
        """Remove requests older than the window."""
        now = time.time()
        return [ts for ts in requests if now - ts < window_seconds]

    def _check_rate_limit(self, client_key: str) -> Optional[JSONResponse]:
        """Check if client has exceeded rate limits. Returns error response if limited."""
        now = time.time()
        state = self.clients[client_key]

        # Clean old requests
        state.minute_requests = self._clean_old_requests(state.minute_requests, 60)
        state.hour_requests = self._clean_old_requests(state.hour_requests, 3600)
        state.burst_requests = self._clean_old_requests(state.burst_requests, 10)

        # Check burst limit (10 second window)
        if len(state.burst_requests) >= self.config.burst_limit:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Burst limit exceeded. Max {self.config.burst_limit} requests per 10 seconds.",
                    "retry_after": 10,
                },
                headers={"Retry-After": "10", "X-RateLimit-Limit": str(self.config.burst_limit)},
            )

        # Check per-minute limit
        if len(state.minute_requests) >= self.config.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Rate limit exceeded. Max {self.config.requests_per_minute} requests per minute.",
                    "retry_after": 60,
                },
                headers={"Retry-After": "60", "X-RateLimit-Limit": str(self.config.requests_per_minute)},
            )

        # Check per-hour limit
        if len(state.hour_requests) >= self.config.requests_per_hour:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Hourly rate limit exceeded. Max {self.config.requests_per_hour} requests per hour.",
                    "retry_after": 3600,
                },
                headers={"Retry-After": "3600", "X-RateLimit-Limit": str(self.config.requests_per_hour)},
            )

        return None

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for exempt paths
        if self._is_exempt(request.url.path):
            return await call_next(request)

        client_key = self._get_client_key(request)

        # Check rate limits
        limit_response = self._check_rate_limit(client_key)
        if limit_response:
            return limit_response

        # Record this request
        now = time.time()
        state = self.clients[client_key]
        state.minute_requests.append(now)
        state.hour_requests.append(now)
        state.burst_requests.append(now)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        state = self.clients[client_key]
        response.headers["X-RateLimit-Limit-Minute"] = str(self.config.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            max(0, self.config.requests_per_minute - len(state.minute_requests))
        )
        response.headers["X-RateLimit-Limit-Hour"] = str(self.config.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            max(0, self.config.requests_per_hour - len(state.hour_requests))
        )

        return response