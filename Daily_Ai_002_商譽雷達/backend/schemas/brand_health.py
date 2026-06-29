from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BrandHealthResponse(BaseModel):
    id: str
    sentiment_index: float = Field(ge=-100, le=100)
    nps_score: Optional[float] = Field(None, ge=-100, le=100)
    reputation_score: Optional[float] = Field(None, ge=0, le=100)
    share_of_voice: Optional[float] = None
    engagement_rate: Optional[float] = None
    alert_count: int = 0
    trend_direction: str = "stable"
    measured_at: datetime


class StoreHealthResponse(BaseModel):
    store_id: str
    store_name: Optional[str] = None
    sentiment_index: float
    nps_score: Optional[float] = None
    csat_score: Optional[float] = None
    alert_count: int = 0
    top_issues: List[str] = Field(default_factory=list)
    staff_sentiment: Optional[float] = None
    measured_at: datetime


class AlertCreate(BaseModel):
    store_id: Optional[str] = None
    title: str = Field(..., min_length=3, max_length=256)
    description: str = Field(..., min_length=1)
    severity: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    category: str = Field(default="general")
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AlertResponse(BaseModel):
    id: str
    store_id: Optional[str] = None
    title: str
    description: str
    severity: str
    category: str
    status: str = "active"
    source: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
