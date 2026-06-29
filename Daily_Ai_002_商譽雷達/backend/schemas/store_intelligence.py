from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StoreDailyIntelligenceRead(BaseModel):
    id: int
    org_id: int
    store_id: int
    store_name: Optional[str] = None
    report_date: date
    store_health_score: float
    cx_score: float
    voc_risk_score: float
    response_quality_score: float
    resolution_rate: float
    operational_risk_score: float
    trend_direction: str
    top_issues: Optional[List[Dict[str, Any]]] = None
    ai_recommendations: Optional[List[Dict[str, Any]]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class StoreDailyIntelligenceList(BaseModel):
    items: List[StoreDailyIntelligenceRead]
    total: int
    page: int
    page_size: int
    total_pages: int


class StoreRankingRead(BaseModel):
    rank: int
    store_id: int
    store_name: str
    health_score: float
    cx_score: float
    risk_score: float
    trend: str
    critical_issues: int


class StoreRankingResponse(BaseModel):
    rankings: List[StoreRankingRead]
    critical_stores: List[StoreRankingRead]
    improving_stores: List[StoreRankingRead]
    declining_stores: List[StoreRankingRead]
    top_store_issues: List[Dict[str, Any]]


class StoreDailyReport(BaseModel):
    store_id: int
    store_name: str
    report_date: date
    store_health_score: float
    cx_score: float
    voc_risk_score: float
    response_quality_score: float
    resolution_rate: float
    operational_risk_score: float
    trend_direction: str
    top_issues: Optional[List[Dict[str, Any]]] = None
    ai_recommendations: Optional[List[Dict[str, Any]]] = None
    yesterday_comparison: Optional[Dict[str, Any]] = None
    specific_recommendations: List[str] = Field(default_factory=list)


class StoreIssueCreate(BaseModel):
    store_id: int
    issue_type: str = Field(..., description="wait_time/service_quality/food_quality/cleanliness/staff_attitude/price/booking/system/other")
    severity: str = Field(default="medium", description="low/medium/high/critical")
    occurrence_count: int = Field(default=1, ge=1)
    affected_touchpoints: Optional[List[str]] = None
    resolution_notes: Optional[str] = None


class StoreIssueResolve(BaseModel):
    resolution_notes: str


class StoreIssueRead(BaseModel):
    id: int
    org_id: int
    store_id: int
    store_name: Optional[str] = None
    issue_type: str
    severity: str
    occurrence_count: int
    affected_touchpoints: Optional[List[str]] = None
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

    model_config = {"from_attributes": True}


class StoreIntelligenceSummary(BaseModel):
    total_stores: int
    average_health_score: float
    average_cx_score: float
    average_voc_risk_score: float
    total_critical_stores: int
    total_improving_stores: int
    total_declining_stores: int
    top_issue_types: List[Dict[str, Any]]
    report_date: date
