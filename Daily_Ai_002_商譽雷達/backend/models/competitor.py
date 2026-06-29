from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, DateTime, Integer, ForeignKey, Float, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class Competitor(Base):
    __tablename__ = "competitors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    metrics: Mapped[List["CompetitorMetric"]] = relationship(back_populates="competitor", lazy="selectin")
    swots: Mapped[List["CompetitorSWOT"]] = relationship(back_populates="competitor", lazy="selectin")

    __table_args__ = (
        {"comment": "Tracked competitors"},
    )


class CompetitorMetric(Base):
    __tablename__ = "competitor_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    competitor_id: Mapped[int] = mapped_column(ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False, index=True)
    google_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    review_volume: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    brand_health: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    share_of_voice: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    competitor: Mapped["Competitor"] = relationship(back_populates="metrics")

    __table_args__ = (
        {"comment": "Time-series competitor metrics"},
    )


class CompetitorSWOT(Base):
    __tablename__ = "competitor_swot"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    competitor_id: Mapped[int] = mapped_column(ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    competitor: Mapped["Competitor"] = relationship(back_populates="swots")

    __table_args__ = (
        {"comment": "SWOT analysis entries for competitors"},
    )
