from datetime import datetime
from typing import Optional, List, Any

from pydantic import BaseModel, Field


class CXJourneyCreate(BaseModel):
    store_id: Optional[int] = None
    customer_id: Optional[str] = Field(None, max_length=100)
    touchpoints: Optional[List[str]] = None
    satisfaction_score: Optional[float] = Field(None, ge=0, le=10)
    effort_score: Optional[float] = Field(None, ge=0, le=10)
    nps_score: Optional[float] = Field(None, ge=-100, le=100)
    completed_at: Optional[datetime] = None


class CXJourneyRead(BaseModel):
    id: int
    org_id: int
    store_id: Optional[int] = None
    customer_id: Optional[str] = None
    touchpoints: Optional[Any] = None
    satisfaction_score: Optional[float] = None
    effort_score: Optional[float] = None
    nps_score: Optional[float] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TouchPointCreate(BaseModel):
    name: str = Field(..., max_length=50)
    satisfaction_score: Optional[float] = Field(None, ge=0, le=10)
    friction_score: Optional[float] = Field(None, ge=0, le=10)
    status: str = Field("healthy", max_length=20)


class TouchPointRead(BaseModel):
    id: int
    org_id: int
    name: str
    satisfaction_score: Optional[float] = None
    friction_score: Optional[float] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CXInsightRead(BaseModel):
    id: int
    org_id: int
    store_id: Optional[int] = None
    touchpoint_id: Optional[int] = None
    insight_type: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    detected_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class JourneyDiagnosticResponse(BaseModel):
    journey_id: int
    overall_satisfaction: float
    effort_score: float
    nps_score: Optional[float] = None
    touchpoints: List[TouchPointRead]
    insights: List[CXInsightRead]
    friction_points: List[dict]
    recommendations: List[str]
