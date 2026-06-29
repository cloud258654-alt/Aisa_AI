"""
Authentication Service
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status

from backend.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    decode_token,
)
from backend.core.config import settings
from backend.models.organization import User

logger = logging.getLogger(__name__)


class AuthService:
    """Handles user authentication, registration, and token management."""

    @staticmethod
    async def authenticate(db: AsyncSession, email: str, password: str) -> dict:
        """Authenticate user with email and password."""
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
            )

        access_token = create_access_token(
            subject=str(user.id),
            extra_claims={
                "email": user.email,
                "role": user.role,
                "organization_id": str(user.org_id) if user.org_id else None,
            },
        )
        refresh_token = create_refresh_token(
            subject=str(user.id),
            extra_claims={
                "email": user.email,
                "role": user.role,
                "organization_id": str(user.org_id) if user.org_id else None,
            },
        )

        logger.info("User authenticated: %s", user.email)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    async def register(db: AsyncSession, user_data) -> User:
        """Register a new user."""
        email = getattr(user_data, "email", None) or user_data.get("email")
        password = getattr(user_data, "password", None) or user_data.get("password")
        full_name = getattr(user_data, "full_name", None) or user_data.get("full_name", "")
        role = getattr(user_data, "role", None) or user_data.get("role", "viewer")
        org_id = getattr(user_data, "org_id", None) or user_data.get("org_id")
        dept_id = getattr(user_data, "dept_id", None) or user_data.get("dept_id")
        store_id = getattr(user_data, "store_id", None) or user_data.get("store_id")

        existing = await db.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email '{email}' already exists",
            )

        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            role=role,
            org_id=int(org_id) if org_id else None,
            dept_id=int(dept_id) if dept_id else None,
            store_id=int(store_id) if store_id else None,
            is_active=True,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        logger.info("User registered: %s", user.email)
        return user

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            uid = int(user_id)
        except (ValueError, TypeError):
            return None

        result = await db.execute(select(User).where(User.id == uid))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_users(
        db: AsyncSession, org_id: str, skip: int = 0, limit: int = 100
    ) -> list:
        """List users in an organization."""
        try:
            oid = int(org_id)
        except (ValueError, TypeError):
            return []

        count_q = select(func.count(User.id)).where(User.org_id == oid)
        total = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            select(User)
            .where(User.org_id == oid)
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        users = result.scalars().all()
        return list(users)

    @staticmethod
    async def update_user(db: AsyncSession, user_id: str, update_data: dict) -> User:
        """Update user profile."""
        try:
            uid = int(user_id)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found",
            )

        result = await db.execute(select(User).where(User.id == uid))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found",
            )

        updatable_fields = {
            "full_name", "email", "dept_id", "store_id",
        }
        for key, value in update_data.items():
            if key in updatable_fields and value is not None:
                if key in ("dept_id", "store_id") and value is not None:
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        continue
                setattr(user, key, value)

        await db.commit()
        await db.refresh(user)

        logger.info("User updated: %s", user.email)
        return user

    @staticmethod
    async def update_user_role(db: AsyncSession, user_id: str, role: str) -> User:
        """Update user role (admin only)."""
        try:
            uid = int(user_id)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found",
            )

        result = await db.execute(select(User).where(User.id == uid))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found",
            )

        valid_roles = {"viewer", "analyst", "manager", "admin", "superadmin"}
        if role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role '{role}'. Valid roles: {', '.join(sorted(valid_roles))}",
            )

        user.role = role
        await db.commit()
        await db.refresh(user)

        logger.info("User role updated: %s -> %s", user.email, role)
        return user

    @staticmethod
    async def refresh_token(db: AsyncSession, refresh_token: str) -> dict:
        """Refresh access token using refresh token."""
        try:
            payload = decode_token(refresh_token)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Expected refresh token.",
            )

        sub = payload.get("sub")
        if not sub:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing subject claim",
            )

        email = payload.get("email", "")
        role = payload.get("role", "viewer")
        org_id = payload.get("organization_id")

        user = await AuthService.get_user_by_id(db, sub)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer exists",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
            )

        access_token = create_access_token(
            subject=sub,
            extra_claims={
                "email": email,
                "role": role,
                "organization_id": org_id,
            },
        )
        new_refresh_token = create_refresh_token(
            subject=sub,
            extra_claims={
                "email": email,
                "role": role,
                "organization_id": org_id,
            },
        )

        logger.info("Token refreshed for user: %s", email)
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
