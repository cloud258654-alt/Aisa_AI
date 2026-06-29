from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from backend.api.deps import RequireRole, get_current_user, pagination_params
from backend.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from backend.schemas.common import PaginatedResponse
from backend.services.auth import AuthService
from backend.models.organization import User
from sqlalchemy import select as sa_select, func as sa_func

router = APIRouter()


def _user_to_response(user) -> Dict[str, Any]:
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "department": None,
        "store_id": str(user.store_id) if user.store_id else None,
        "organization_id": str(user.org_id) if user.org_id else None,
        "is_active": user.is_active,
        "avatar_url": None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login_at": user.updated_at.isoformat() if user.updated_at else None,
    }


# ---------------------------------------------------------------------------
# POST /login
# ---------------------------------------------------------------------------
@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login and obtain access/refresh tokens",
    description="Authenticate with email and password to receive a JWT token pair.",
)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    return await AuthService.authenticate(db, body.email, body.password)


# ---------------------------------------------------------------------------
# POST /refresh
# ---------------------------------------------------------------------------
@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access token pair.",
)
async def refresh_token(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    return await AuthService.refresh_token(db, body.refresh_token)


# ---------------------------------------------------------------------------
# POST /register
# ---------------------------------------------------------------------------
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user (admin only)",
    description="Create a new user account. Requires admin or superadmin role.",
    dependencies=[Depends(RequireRole("admin", "superadmin"))],
)
async def register(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    user = await AuthService.register(db, body)
    return _user_to_response(user)


# ---------------------------------------------------------------------------
# GET /me
# ---------------------------------------------------------------------------
@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
)
async def get_me(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    user = await AuthService.get_user_by_id(db, current_user["id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return _user_to_response(user)


# ---------------------------------------------------------------------------
# PUT /me
# ---------------------------------------------------------------------------
@router.put(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
)
async def update_me(
    body: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    update_dict = body.model_dump(exclude_unset=True)
    updated = await AuthService.update_user(db, current_user["id"], update_dict)
    return _user_to_response(updated)


# ---------------------------------------------------------------------------
# GET /users
# ---------------------------------------------------------------------------
@router.get(
    "/users",
    response_model=PaginatedResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List all users (admin only)",
    dependencies=[Depends(RequireRole("admin", "superadmin"))],
)
async def list_users(
    pagination: Dict[str, int] = Depends(pagination_params),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    org_id = current_user.get("organization_id", "")
    page = pagination["page"]
    page_size = pagination["page_size"]
    skip = (page - 1) * page_size

    user_list = await AuthService.list_users(db, org_id, skip=skip, limit=page_size)

    total = len(user_list)
    if org_id:
        try:
            count_result = await db.execute(
                sa_select(sa_func.count()).select_from(User).where(User.org_id == int(org_id))
            )
            total = count_result.scalar() or len(user_list)
        except (ValueError, TypeError):
            pass

    return {
        "items": [_user_to_response(u) for u in user_list],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }


# ---------------------------------------------------------------------------
# PUT /users/{user_id}/role
# ---------------------------------------------------------------------------
@router.put(
    "/users/{user_id}/role",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a user's role (admin only)",
    dependencies=[Depends(RequireRole("admin", "superadmin"))],
)
async def update_user_role(
    user_id: str,
    role: str = "user",
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    updated = await AuthService.update_user_role(db, user_id, role)
    return _user_to_response(updated)
