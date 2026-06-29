"""Rate limiting middleware using Redis sliding window."""
import time
import logging
from typing import Callable, Dict, Optional

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from backend.core.redis import get_redis

logger = logging.getLogger(__name__)

DEFAULT_LIMIT = 100
DEFAULT_WINDOW_SECONDS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter backed by Redis.

    Configurable per-route via *limit* and *window_seconds*.
    """

    def __init__(
        self,
        app,
        global_limit: int = DEFAULT_LIMIT,
        global_window_seconds: int = DEFAULT_WINDOW_SECONDS,
        route_limits: Optional[Dict[str, int]] = None,
    ) -> None:
        super().__init__(app)
        self.global_limit = global_limit
        self.global_window_seconds = global_window_seconds
        self.route_limits = route_limits or {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_key = self._build_key(request)

        limit = self.global_limit
        window = self.global_window_seconds

        for prefix, route_limit in self.route_limits.items():
            if request.url.path.startswith(prefix):
                limit = route_limit
                break

        allowed = await self._check_limit(client_key, limit, window)
        if not allowed:
            logger.warning("Rate limit exceeded for key=%s path=%s", client_key, request.url.path)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try again later.",
                headers={"Retry-After": str(window)},
            )

        response: Response = await call_next(request)
        remaining = await self._get_remaining(client_key, limit, window)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(remaining, 0))
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + window)
        return response

    def _build_key(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        return f"rate_limit:{client_ip}:{request.url.path}"

    async def _check_limit(self, key: str, limit: int, window: int) -> bool:
        now_ms = int(time.time() * 1000)
        window_start = now_ms - (window * 1000)

        try:
            redis_gen = get_redis()
            redis_client = await redis_gen.__anext__()
        except Exception:
            return True

        try:
            async with redis_client.pipeline(transaction=True) as pipe:
                pipe.zremrangebyscore(key, 0, window_start)
                pipe.zcard(key)
                pipe.zadd(key, {str(now_ms): now_ms})
                pipe.expire(key, window + 1)
                _, current_count, _, _ = await pipe.execute()

            return current_count < limit
        except Exception as exc:
            logger.error("Redis rate-limit error: %s", exc)
            return True

    async def _get_remaining(self, key: str, limit: int, window: int) -> int:
        now_ms = int(time.time() * 1000)
        window_start = now_ms - (window * 1000)

        try:
            redis_gen = get_redis()
            redis_client = await redis_gen.__anext__()
        except Exception:
            return limit

        try:
            async with redis_client.pipeline(transaction=True) as pipe:
                pipe.zremrangebyscore(key, 0, window_start)
                pipe.zcard(key)
                _, count = await pipe.execute()
            return limit - count
        except Exception:
            return limit
