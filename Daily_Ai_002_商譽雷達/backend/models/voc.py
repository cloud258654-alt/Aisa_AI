from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class VoiceSource(Base):
    __tablename__ = "voice_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id", ondelete="SET NULL"), nullable=True, index=True)
    channel: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    author_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    analyses: Mapped[List["VoiceAnalysis"]] = relationship(back_populates="voice_source", lazy="selectin")
    cases: Mapped[List["Case"]] = relationship(back_populates="voice_source", lazy="selectin")

    __table_args__ = (
        {"comment": "Raw customer feedback from all channels"},
    )


class VoiceAnalysis(Base):
    __tablename__ = "voice_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    voice_source_id: Mapped[int] = mapped_column(ForeignKey("voice_sources.id", ondelete="CASCADE"), nullable=False, index=True)
    sentiment: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=False)
    emotion: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    topic: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    journey_touchpoint: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pain_point_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    intent: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    need_detected: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    risk_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    risk_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    voice_source: Mapped["VoiceSource"] = relationship(back_populates="analyses")

    __table_args__ = (
        {"comment": "AI-analyzed insights from voice sources"},
    )


class VoiceTag(Base):
    __tablename__ = "voice_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    color: Mapped[str] = mapped_column(String(7), default="#6366f1", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"comment": "Tags for categorizing voice data"},
    )
