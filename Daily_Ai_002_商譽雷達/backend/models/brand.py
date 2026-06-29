from datetime import datetime, date
from typing import Optional

from sqlalchemy import String, DateTime, Integer, ForeignKey, Float, Date, Boolean, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class BrandHealth(Base):
    __tablename__ = "brand_health"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    calculated_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    brand_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    store_health_index: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    csat_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    resolution_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reputation_risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    brand_momentum: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"comment": "Daily snapshot of overall brand health metrics"},
    )


class StoreHealth(Base):
    __tablename__ = "store_health"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    calculated_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    store_health_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    csat_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    review_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    avg_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    negative_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    response_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    resolution_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"comment": "Per-store health metrics snapshot"},
    )


class BrandAlert(Base):
    __tablename__ = "brand_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id", ondelete="SET NULL"), nullable=True, index=True)
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        {"comment": "Brand health alerts and notifications"},
    )
