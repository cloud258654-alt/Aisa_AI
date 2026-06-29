from __future__ import annotations

import os
from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/sentinel_ecxip"

    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str

    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    ENVIRONMENT: str = "development"

    DEMO_MODE: bool = True

    VERSION: str = "1.0.0"

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]

    OPENAI_API_KEY: Optional[str] = None

    GEMINI_API_KEY: Optional[str] = None

    CELERY_BROKER_URL: str = "redis://localhost:6379/1"

    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    SENTRY_DSN: Optional[str] = None

    LOG_LEVEL: str = "INFO"

    API_V1_PREFIX: str = "/api/v1"

    PROJECT_NAME: str = "Sentinel AI ECXIP"

    PROJECT_VERSION: str = "1.0.0"

    PROJECT_DESCRIPTION: str = (
        "Customer Experience Intelligence Platform — "
        "Real-time sentiment analysis, voice emotion detection, "
        "and multi-channel feedback aggregation."
    )

    STATIC_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static")

    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"

    @property
    def database_url_sync(self) -> str:
        return self.DATABASE_URL.replace("+asyncpg", "+psycopg2")

    @property
    def cors_origins_combined(self) -> List[str]:
        return list(set(self.CORS_ORIGINS + self.BACKEND_CORS_ORIGINS))


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
