from __future__ import annotations

from typing import AsyncGenerator, Optional

import redis.asyncio as redis

from core.config import settings

_redis_client: Optional[redis.Redis] = None


def get_redis_sync() -> redis.Redis:
    import redis as sync_redis

    return sync_redis.from_url(settings.REDIS_URL, decode_responses=True)


async def init_redis() -> None:
    global _redis_client
    _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


async def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None


async def check_redis_health() -> bool:
    try:
        client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        await client.ping()
        await client.aclose()
        return True
    except Exception:
        return False


async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    if _redis_client is not None:
        yield _redis_client
    else:
        client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        try:
            yield client
        finally:
            await client.aclose()
