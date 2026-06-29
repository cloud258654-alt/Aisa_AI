from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RootCauseItem(BaseModel):
    cause: str
    frequency: int
    impact_score: float
    percentage: float
    affected_stores: List[str] = Field(default_factory=list)
    suggested_actions: List[str] = Field(default_factory=list)


class RootCauseAnalysisCreate(BaseModel):
    case_id: Optional[str] = None
    incident_type: str
    store_id: Optional[str] = None
    description: str = Field(..., min_length=1)
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    analysis_depth: str = Field(default="standard", pattern="^(quick|standard|deep)$")
    include_competitor_data: bool = False


class RootCauseAnalysisResponse(BaseModel):
    id: str
    case_id: Optional[str] = None
    incident_type: str
    store_id: Optional[str] = None
    status: str = "pending"
    root_causes: List[RootCauseItem] = Field(default_factory=list)
    confidence_score: Optional[float] = None
    summary: Optional[str] = None
    methodology: Optional[str] = None
    triggered_by: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime


class RootCauseSummaryResponse(BaseModel):
    total_analyses: int
    top_causes: List[RootCauseItem]
    pareto_data: List[Dict[str, Any]] = Field(default_factory=list)
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    generated_at: datetime
