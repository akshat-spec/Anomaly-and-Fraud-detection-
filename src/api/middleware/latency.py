"""Middleware to measure and log slow API request latencies."""

import logging
import time
from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("fraud_api.latency")


class LatencyLoggingMiddleware(BaseHTTPMiddleware):
    """Tracks latency for each request and logs a WARNING if it exceeds 200ms."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.perf_counter()
        
        # Inject start time into state for route handlers to access
        request.state.start_time = start_time

        try:
            response = await call_next(request)
        finally:
            process_time_ms = (time.perf_counter() - start_time) * 1000.0
            
            # Log slow requests
            if process_time_ms > 200.0:
                logger.warning(
                    "Slow request detected",
                    extra={
                        "path": request.url.path,
                        "method": request.method,
                        "client": request.client.host if request.client else "unknown",
                        "latency_ms": round(process_time_ms, 2),
                    },
                )
                
            # Optionally add a header to the response
            if 'response' in locals():
                response.headers["X-Process-Time"] = str(process_time_ms)

        return response
