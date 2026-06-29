from __future__ import annotations

from datetime import date, datetime, time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# OperationalMetric
# ---------------------------------------------------------------------------
class OperationalMetricCreate(BaseModel):
    store_id: int
    metric_type: str = Field(..., max_length=50)
    metric_value: float
    recorded_at: Optional[datetime] = None


class OperationalMetricRead(BaseModel):
    id: int
    org_id: int
    store_id: int
    metric_type: str
    metric_value: float
    recorded_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class OperationalMetricList(BaseModel):
    items: List[OperationalMetricRead]
    total: int
    page: int
    page_size: int


# ---------------------------------------------------------------------------
# StaffSchedule
# ---------------------------------------------------------------------------
class StaffScheduleCreate(BaseModel):
    store_id: int
    shift_date: date
    shift_type: str = Field(..., max_length=20)
    staff_count: int = Field(..., ge=0)
    peak_hour_start: Optional[str] = Field(None, max_length=5)
    peak_hour_end: Optional[str] = Field(None, max_length=5)


class StaffScheduleRead(BaseModel):
    id: int
    org_id: int
    store_id: int
    shift_date: date
    shift_type: str
    staff_count: int
    peak_hour_start: Optional[str] = None
    peak_hour_end: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# StoreTraffic
# ---------------------------------------------------------------------------
class StoreTrafficCreate(BaseModel):
    store_id: int
    hour: datetime
    visitor_count: int = Field(..., ge=0)
    peak_flag: bool = False
    weather_condition: Optional[str] = Field(None, max_length=50)
    is_holiday: bool = False


class StoreTrafficRead(BaseModel):
    id: int
    org_id: int
    store_id: int
    hour: datetime
    visitor_count: int
    peak_flag: bool
    weather_condition: Optional[str] = None
    is_holiday: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Campaign
# ---------------------------------------------------------------------------
class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    campaign_type: str = Field(..., max_length=50)
    store_ids: List[int] = Field(..., min_length=1)
    start_date: date
    end_date: date
    discount_rate: Optional[float] = Field(None, ge=0, le=100)
    is_active: bool = True


class CampaignRead(BaseModel):
    id: int
    org_id: int
    name: str
    campaign_type: str
    store_ids: List[int]
    start_date: date
    end_date: date
    discount_rate: Optional[float] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Operational Summary & Analysis
# ---------------------------------------------------------------------------
class MetricCorrelation(BaseModel):
    metric: str
    value: float
    relationship: str


class BusinessRecommendation(BaseModel):
    action: str
    expected_impact: str
    priority: str = Field(default="medium", pattern="^(low|medium|high|critical)$")


class OperationalSummary(BaseModel):
    store_id: int
    current_metrics: Dict[str, Any] = Field(default_factory=dict)
    correlations: List[MetricCorrelation] = Field(default_factory=list)
    recommendations: List[BusinessRecommendation] = Field(default_factory=list)


class OperationalAnalyzeRequest(BaseModel):
    store_id: int
    event_description: str = Field(..., min_length=3)
    date_range: Optional[Dict[str, Optional[date]]] = None


class DataCorrelation(BaseModel):
    metric: str
    value: float
    relationship: str


class OperationalAnalyzeResponse(BaseModel):
    event_summary: str
    data_correlations: List[DataCorrelation] = Field(default_factory=list)
    root_cause_analysis: str
    business_recommendations: List[BusinessRecommendation] = Field(default_factory=list)
