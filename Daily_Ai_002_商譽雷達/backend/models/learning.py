from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, DateTime, Integer, ForeignKey, Float, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class LearningCase(Base):
    __tablename__ = "learning_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    case_title: Mapped[str] = mapped_column(String(500), nullable=False)
    case_description: Mapped[str] = mapped_column(Text, nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id", ondelete="SET NULL"), nullable=True, index=True)
    resolution_action: Mapped[str] = mapped_column(Text, nullable=False)
    resolution_outcome: Mapped[str] = mapped_column(Text, nullable=False)
    success_rating: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    embedding_vector: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    similar_case_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    store: Mapped[Optional["Store"]] = relationship(lazy="selectin")
    outcomes: Mapped[List["RecommendationOutcome"]] = relationship(back_populates="case", lazy="selectin")
    from_links: Mapped[List["SimilarCaseLink"]] = relationship(foreign_keys="SimilarCaseLink.case_a_id", back_populates="case_a", lazy="selectin")
    to_links: Mapped[List["SimilarCaseLink"]] = relationship(foreign_keys="SimilarCaseLink.case_b_id", back_populates="case_b", lazy="selectin")

    __table_args__ = (
        {"comment": "Resolved cases stored as organizational learning knowledge"},
    )


class LearningPattern(Base):
    __tablename__ = "learning_patterns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    pattern_name: Mapped[str] = mapped_column(String(500), nullable=False)
    pattern_description: Mapped[str] = mapped_column(Text, nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    frequency: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    success_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    recommended_actions: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"comment": "Discovered patterns from aggregated learning cases"},
    )


class RecommendationOutcome(Base):
    __tablename__ = "recommendation_outcomes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    recommendation_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("learning_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    action_taken: Mapped[str] = mapped_column(Text, nullable=False)
    outcome: Mapped[str] = mapped_column(Text, nullable=False)
    effectiveness_score: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    feedback_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    case: Mapped["LearningCase"] = relationship(back_populates="outcomes")

    __table_args__ = (
        {"comment": "Tracked outcomes of recommendations applied from learning cases"},
    )


class SimilarCaseLink(Base):
    __tablename__ = "similar_case_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_a_id: Mapped[int] = mapped_column(ForeignKey("learning_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    case_b_id: Mapped[int] = mapped_column(ForeignKey("learning_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    relationship_type: Mapped[str] = mapped_column(String(30), nullable=False, default="same_issue")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    case_a: Mapped["LearningCase"] = relationship(foreign_keys=[case_a_id], back_populates="from_links")
    case_b: Mapped["LearningCase"] = relationship(foreign_keys=[case_b_id], back_populates="to_links")

    __table_args__ = (
        {"comment": "Similarity relationships between learning cases"},
    )
