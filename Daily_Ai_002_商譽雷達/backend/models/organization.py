import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey, Text, JSON, Table, Column, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


user_role_table = Table(
    "user_role",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    plan: Mapped[str] = mapped_column(String(20), default="free", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    departments: Mapped[List["Department"]] = relationship(back_populates="organization", lazy="selectin")
    regions: Mapped[List["Region"]] = relationship(back_populates="organization", lazy="selectin")
    stores: Mapped[List["Store"]] = relationship(back_populates="organization", lazy="selectin")
    users: Mapped[List["User"]] = relationship(back_populates="organization", lazy="selectin")
    roles: Mapped[List["Role"]] = relationship(back_populates="organization", lazy="selectin")

    __table_args__ = (
        {"comment": "Multi-tenant organizations (tenants)"},
    )


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    organization: Mapped["Organization"] = relationship(back_populates="departments")
    parent: Mapped[Optional["Department"]] = relationship(remote_side="Department.id", back_populates="children", lazy="selectin")
    children: Mapped[List["Department"]] = relationship(back_populates="parent", lazy="selectin")
    stores: Mapped[List["Store"]] = relationship(back_populates="department", lazy="selectin")
    users: Mapped[List["User"]] = relationship(back_populates="department", lazy="selectin")

    __table_args__ = (
        {"comment": "Organizational departments"},
    )


class Region(Base):
    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    organization: Mapped["Organization"] = relationship(back_populates="regions")
    stores: Mapped[List["Store"]] = relationship(back_populates="region", lazy="selectin")

    __table_args__ = (
        {"comment": "Geographic regions within an organization"},
    )


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    dept_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True)
    region_id: Mapped[Optional[int]] = mapped_column(ForeignKey("regions.id", ondelete="SET NULL"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    manager_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    organization: Mapped["Organization"] = relationship(back_populates="stores")
    department: Mapped[Optional["Department"]] = relationship(back_populates="stores")
    region: Mapped[Optional["Region"]] = relationship(back_populates="stores")
    users: Mapped[List["User"]] = relationship(back_populates="store", lazy="selectin")

    __table_args__ = (
        {"comment": "Physical or virtual store locations"},
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="viewer", nullable=False)
    dept_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True)
    store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id", ondelete="SET NULL"), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    organization: Mapped["Organization"] = relationship(back_populates="users")
    department: Mapped[Optional["Department"]] = relationship(back_populates="users")
    store: Mapped[Optional["Store"]] = relationship(back_populates="users")
    roles: Mapped[List["Role"]] = relationship(secondary=user_role_table, back_populates="users", lazy="selectin")
    assigned_cases: Mapped[List["Case"]] = relationship(foreign_keys="Case.assigned_to", back_populates="assignee", lazy="selectin")
    created_cases: Mapped[List["Case"]] = relationship(foreign_keys="Case.created_by", back_populates="creator", lazy="selectin")
    case_timelines: Mapped[List["CaseTimeline"]] = relationship(back_populates="performer", lazy="selectin")

    __table_args__ = (
        {"comment": "Platform users scoped to an organization"},
    )


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    permissions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    organization: Mapped["Organization"] = relationship(back_populates="roles")
    users: Mapped[List["User"]] = relationship(secondary=user_role_table, back_populates="roles", lazy="selectin")

    __table_args__ = (
        {"comment": "Custom roles with JSON permissions"},
    )
