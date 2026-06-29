from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, Float, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class CXJourney(Base):
    __tablename__ = "cx_journeys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id", ondelete="SET NULL"), nullable=True, index=True)
    customer_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    touchpoints: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    satisfaction_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    effort_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    nps_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"comment": "End-to-end customer journey records"},
    )


class TouchPoint(Base):
    __tablename__ = "touch_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    satisfaction_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    friction_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="healthy", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    insights: Mapped[List["CXInsight"]] = relationship(back_populates="touchpoint", lazy="selectin")

    __table_args__ = (
        {"comment": "Customer experience touchpoint definitions"},
    )


class CXInsight(Base):
    __tablename__ = "cx_insights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id", ondelete="SET NULL"), nullable=True, index=True)
    touchpoint_id: Mapped[Optional[int]] = mapped_column(ForeignKey("touch_points.id", ondelete="SET NULL"), nullable=True, index=True)
    insight_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    detected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    touchpoint: Mapped[Optional["TouchPoint"]] = relationship(back_populates="insights")

    __table_args__ = (
        {"comment": "AI-detected CX insights and anomalies"},
    )
