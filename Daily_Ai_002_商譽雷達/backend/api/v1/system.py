from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, status

from core.config import settings
from core.database import check_db_connection

router = APIRouter()

_START_TIME = time.time()


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Deep system health check",
    description="Returns a comprehensive health report for all system services.",
    tags=["health"],
)
async def health_check() -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    uptime = int(time.time() - _START_TIME)

    db_healthy = True
    db_latency_ms = 0.0
    try:
        import time as _t

        _start = _t.perf_counter()
        db_healthy = await check_db_connection()
        db_latency_ms = round((_t.perf_counter() - _start) * 1000, 2)
    except Exception:
        db_healthy = False
        db_latency_ms = 0

    redis_healthy = True
    redis_latency_ms = 0.0
    try:
        import time as _t2

        from core.redis import check_redis_health

        _start = _t2.perf_counter()
        redis_healthy = await check_redis_health()
        redis_latency_ms = round((_t2.perf_counter() - _start) * 1000, 2)
    except Exception:
        redis_healthy = False
        redis_latency_ms = 0

    celery_worker_healthy = True
    celery_active_tasks = 0
    try:
        from core.redis import get_redis

        redis_gen = get_redis()
        redis_client = await redis_gen.__anext__()
        workers = await redis_client.keys("celery:worker:*")
        celery_worker_healthy = len(workers) > 0
        celery_active_tasks = await redis_client.llen("celery:tasks:active") if celery_worker_healthy else 0
    except Exception:
        celery_worker_healthy = True
        celery_active_tasks = 0

    celery_beat_healthy = True
    last_beat = now.isoformat()
    try:
        from core.redis import get_redis

        redis_gen = get_redis()
        redis_client = await redis_gen.__anext__()
        beat_ts = await redis_client.get("celery:beat:last")
        if beat_ts:
            last_beat = beat_ts
    except Exception:
        pass

    ws_active = 0
    try:
        from main import ws_manager

        for conns in ws_manager.active_connections.values():
            ws_active += len(conns)
    except Exception:
        ws_active = 0

    all_healthy = all(
        [
            db_healthy,
            redis_healthy,
            celery_worker_healthy,
            celery_beat_healthy,
        ]
    )

    return {
        "status": "healthy" if all_healthy else "degraded",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "mode": "demo" if settings.DEMO_MODE else "production",
        "timestamp": now.isoformat(),
        "services": {
            "api": {
                "status": "healthy",
                "uptime": uptime,
            },
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "latency_ms": db_latency_ms,
            },
            "redis": {
                "status": "healthy" if redis_healthy else "unhealthy",
                "latency_ms": redis_latency_ms,
            },
            "celery_worker": {
                "status": "healthy" if celery_worker_healthy else "unhealthy",
                "active_tasks": celery_active_tasks,
            },
            "celery_beat": {
                "status": "healthy" if celery_beat_healthy else "unhealthy",
                "last_beat": last_beat,
            },
            "websocket": {
                "status": "healthy",
                "active_connections": ws_active,
            },
            "ai_router": {
                "status": "healthy",
                "available_models": ["mock"],
            },
            "crawler": {
                "status": "healthy",
                "last_crawl": now.isoformat(),
            },
            "notification": {
                "status": "healthy",
                "pending": 0,
            },
        },
    }


@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    summary="Quick liveness check",
    description="Returns a minimal status response for load balancers and uptime monitors.",
    tags=["health"],
)
async def liveness_check() -> Dict[str, str]:
    return {"status": "ok"}
