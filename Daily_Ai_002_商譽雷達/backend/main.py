from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, List

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from starlette.middleware.base import BaseHTTPMiddleware

from core.config import settings
from core.database import check_db_connection, dispose_engine
from core.redis import check_redis_health, close_redis, init_redis

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


class WebSocketConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str = "default") -> None:
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)
        logger.info(f"WebSocket connected to channel '{channel}' — total: {len(self.active_connections[channel])}")

    def disconnect(self, websocket: WebSocket, channel: str = "default") -> None:
        if channel in self.active_connections:
            try:
                self.active_connections[channel].remove(websocket)
            except ValueError:
                pass
            logger.info(f"WebSocket disconnected from channel '{channel}' — remaining: {len(self.active_connections[channel])}")

    async def broadcast(self, message: dict, channel: str = "default") -> None:
        if channel not in self.active_connections:
            return
        disconnected: List[WebSocket] = []
        import json as _json

        payload = _json.dumps(message, default=str)
        for connection in self.active_connections[channel]:
            try:
                await connection.send_text(payload)
            except Exception:
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn, channel)


ws_manager = WebSocketConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting Sentinel AI ECXIP backend...")

    await init_redis()
    db_ok = await check_db_connection()
    redis_ok = await check_redis_health()

    logger.info(f"Database connection: {'OK' if db_ok else 'FAILED'}")
    logger.info(f"Redis connection:    {'OK' if redis_ok else 'FAILED'}")

    yield

    logger.info("Shutting down Sentinel AI ECXIP backend...")
    await close_redis()
    await dispose_engine()
    logger.info("Shutdown complete.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
    openapi_tags=[
        {"name": "auth", "description": "Authentication & authorization endpoints."},
        {"name": "users", "description": "User management and profile operations."},
        {"name": "organizations", "description": "Organization / tenant management."},
        {"name": "feedback", "description": "Multi-channel feedback ingestion."},
        {"name": "analysis", "description": "Sentiment, emotion, and trend analysis."},
        {"name": "voice", "description": "Real-time voice emotion detection."},
        {"name": "reports", "description": "Dashboards, exports, and scheduled reports."},
        {"name": "integrations", "description": "Third-party API integrations."},
        {"name": "health", "description": "System health and monitoring."},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_combined,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Remaining", "X-RateLimit-Reset", "X-Demo-Mode"],
)


class DemoModeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Demo-Mode"] = "true" if settings.DEMO_MODE else "false"
        return response


app.add_middleware(DemoModeMiddleware)


@app.get(f"{settings.API_V1_PREFIX}/health", tags=["health"])
async def health_check() -> JSONResponse:
    db_status = await check_db_connection()
    redis_status = await check_redis_health()

    overall_healthy = db_status and redis_status
    status_code = 200 if overall_healthy else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if overall_healthy else "unhealthy",
            "version": settings.PROJECT_VERSION,
            "environment": settings.ENVIRONMENT,
            "checks": {
                "database": "ok" if db_status else "error",
                "redis": "ok" if redis_status else "error",
            },
        },
    )


@app.websocket("/ws/voice-stream/{channel}")
async def voice_stream_endpoint(websocket: WebSocket, channel: str) -> None:
    await ws_manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.broadcast({"channel": channel, "type": "voice_chunk", "data": data}, channel)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel)
    except Exception as exc:
        logger.error(f"WebSocket error on channel '{channel}': {exc}")
        ws_manager.disconnect(websocket, channel)


@app.websocket("/ws/alerts/{user_id}")
async def alerts_websocket_endpoint(websocket: WebSocket, user_id: str) -> None:
    channel = f"alerts:{user_id}"
    await ws_manager.connect(websocket, channel)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.broadcast({"channel": channel, "type": "alert_ack", "data": data}, channel)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel)
    except Exception as exc:
        logger.error(f"WebSocket error on alerts channel '{channel}': {exc}")
        ws_manager.disconnect(websocket, channel)


@app.get("/", include_in_schema=False)
async def root() -> HTMLResponse:
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{settings.PROJECT_NAME}</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                   max-width: 800px; margin: 80px auto; padding: 20px; background: #0d1117; color: #c9d1d9; }}
            h1 {{ color: #58a6ff; }}
            .status {{ display: flex; gap: 16px; margin: 24px 0; }}
            .badge {{ padding: 6px 14px; border-radius: 20px; font-size: 13px; background: #21262d; border: 1px solid #30363d; }}
            .badge.green {{ border-color: #238636; color: #3fb950; }}
            a {{ color: #58a6ff; }}
            code {{ background: #161b22; padding: 2px 6px; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <h1>Sentinel AI ECXIP</h1>
        <p>Customer Experience Intelligence Platform — v{settings.PROJECT_VERSION}</p>
        <div class="status">
            <span class="badge green">API Online</span>
            <span class="badge">Environment: {settings.ENVIRONMENT}</span>
        </div>
        <p>API Docs: <a href="/docs">/docs</a> | <a href="/redoc">/redoc</a></p>
        <p>Health: <a href="{settings.API_V1_PREFIX}/health">/api/v1/health</a></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


STATIC_DIR = settings.STATIC_DIR
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

try:
    from api.v1.router import api_v1_router
    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
    logger.info("Consolidated API v1 router mounted successfully.")
except ImportError as exc:
    logger.warning(f"Consolidated API v1 router could not be imported (expected until implemented): {exc}")

try:
    from api.v1 import feedback, analysis, voice, reports
    app.include_router(feedback.router, prefix=f"{settings.API_V1_PREFIX}/feedback", tags=["feedback"])
    app.include_router(analysis.router, prefix=f"{settings.API_V1_PREFIX}/analysis", tags=["analysis"])
    app.include_router(voice.router, prefix=f"{settings.API_V1_PREFIX}/voice", tags=["voice"])
    app.include_router(reports.router, prefix=f"{settings.API_V1_PREFIX}/reports", tags=["reports"])
    logger.info("Legacy API v1 routers mounted successfully.")
except ImportError as exc:
    logger.warning(f"Some legacy API v1 routers could not be imported (expected until implemented): {exc}")
