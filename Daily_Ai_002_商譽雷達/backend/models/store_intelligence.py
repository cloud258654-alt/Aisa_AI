from datetime import datetime, date
from typing import Optional, List

from sqlalchemy import String, DateTime, Integer, ForeignKey, Float, Date, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class StoreDailyIntelligence(Base):
    __tablename__ = "store_daily_intelligence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    report_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    store_health_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cx_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    voc_risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    response_quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    resolution_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    operational_risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    trend_direction: Mapped[str] = mapped_column(String(20), nullable=False, default="stable")
    top_issues: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    ai_recommendations: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    store: Mapped["Store"] = relationship(lazy="selectin")

    __table_args__ = (
        {"comment": "Daily per-store intelligence composite scores and AI recommendations"},
    )


class StoreRanking(Base):
    __tablename__ = "store_rankings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    report_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    overall_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    health_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    cx_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    store: Mapped["Store"] = relationship(lazy="selectin")

    __table_args__ = (
        {"comment": "Store ranking positions across multiple dimensions"},
    )


class StoreIssue(Base):
    __tablename__ = "store_issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    issue_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    occurrence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    affected_touchpoints: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    store: Mapped["Store"] = relationship(lazy="selectin")

    __table_args__ = (
        {"comment": "Detected store-level issues requiring attention"},
    )
