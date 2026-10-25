from collections import defaultdict
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import cast

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.privacy import hash_ip


class RateLimitMiddleware(BaseHTTPMiddleware):
    """In-memory rate limiter middleware (per IP + path)."""

    def __init__(self, app: Callable, limit_per_min: int = 10):
        super().__init__(app)
        self.limit_per_min = limit_per_min
        self._store: dict[tuple[str, str], list[datetime]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        ip = request.client.host if request.client else "unknown"
        path = request.url.path
        key = (hash_ip(ip), path)
        now = datetime.now(UTC)
        window_start = now - timedelta(minutes=1)

        arr = self._store[key]
        arr = [t for t in arr if t > window_start]
        if len(arr) >= self.limit_per_min:
            self._store[key] = arr
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
            )
        arr.append(now)
        self._store[key] = arr

        return cast(Response, await call_next(request))
