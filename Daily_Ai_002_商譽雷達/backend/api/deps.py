from __future__ import annotations

import logging
from datetime import date, datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type

from fastapi import Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.redis import get_redis
from core.security import oauth2_scheme, verify_access_token
from backend.services.auth import AuthService

logger = logging.getLogger(__name__)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Resolve the current authenticated user from JWT and database."""
    payload = verify_access_token(token)
    user_id: str = payload.get("sub", "")

    user = await AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return {
        "id": str(user.id),
        "email": user.email,
        "role": user.role,
        "organization_id": str(user.org_id) if user.org_id else None,
        "claims": payload,
    }


class RequireRole:
    """Class-based role requirement dependency.

    Usage:
        router.get("/users", dependencies=[Depends(RequireRole("admin"))])
        admin_user: dict = Depends(RequireRole("admin", "superadmin"))
    """

    def __init__(self, *allowed_roles: str) -> None:
        self.allowed_roles = allowed_roles

    def __call__(
        self, current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        user_role = current_user.get("role", "user")
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(self.allowed_roles)}",
            )
        return current_user


async def get_tenant_id(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Optional[str]:
    """Extract the tenant (organization) ID from the current user context."""
    return current_user.get("organization_id")


class ChannelFilter(str, Enum):
    email = "email"
    chat = "chat"
    phone = "phone"
    social = "social"
    survey = "survey"
    in_store = "in_store"
    app = "app"
    all = "all"


class SentimentFilter(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"
    all = "all"


class RiskLevelFilter(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"
    all = "all"


class DateRange(str, Enum):
    today = "today"
    yesterday = "yesterday"
    last_7d = "last_7d"
    last_30d = "last_30d"
    last_90d = "last_90d"
    last_1y = "last_1y"
    custom = "custom"


def pagination_params(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
) -> Dict[str, int]:
    """Common pagination dependency returning page and page_size."""
    return {"page": page, "page_size": page_size}


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Unhandled exception on %s %s: %s",
        request.method,
        request.url.path,
        str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "internal_server_error",
                "message": "An unexpected error occurred. Please try again later.",
            },
        },
    )


def common_query_params(
    date_from: Optional[date] = Query(
        default=None,
        description="Filter records from this date (inclusive)",
    ),
    date_to: Optional[date] = Query(
        default=None,
        description="Filter records up to this date (inclusive)",
    ),
    store_id: Optional[str] = Query(
        default=None,
        description="Filter by store ID",
    ),
    channel: Optional[ChannelFilter] = Query(
        default=None,
        description="Filter by feedback channel",
    ),
    sentiment: Optional[SentimentFilter] = Query(
        default=None,
        description="Filter by sentiment",
    ),
    risk_level: Optional[RiskLevelFilter] = Query(
        default=None,
        description="Filter by risk level",
    ),
    keyword: Optional[str] = Query(
        default=None,
        description="Search keyword in content",
    ),
    sort_by: Optional[str] = Query(
        default="created_at",
        description="Field to sort by",
    ),
    sort_order: Optional[str] = Query(
        default="desc",
        pattern="^(asc|desc)$",
        description="Sort order: asc or desc",
    ),
) -> Dict[str, Any]:
    """Common query parameter dependency for filtering list endpoints."""
    return {
        "date_from": date_from,
        "date_to": date_to,
        "store_id": store_id,
        "channel": channel.value if channel else None,
        "sentiment": sentiment.value if sentiment else None,
        "risk_level": risk_level.value if risk_level else None,
        "keyword": keyword,
        "sort_by": sort_by,
        "sort_order": sort_order,
    }
