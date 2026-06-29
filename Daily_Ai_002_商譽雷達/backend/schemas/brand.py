from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, Field


class BrandHealthRead(BaseModel):
    id: int
    org_id: int
    calculated_date: date
    brand_score: Optional[float] = None
    store_health_index: Optional[float] = None
    csat_score: Optional[float] = None
    resolution_rate: Optional[float] = None
    reputation_risk_score: Optional[float] = None
    brand_momentum: Optional[float] = None
    calculated_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class StoreHealthRead(BaseModel):
    id: int
    org_id: int
    store_id: int
    calculated_date: date
    store_health_score: Optional[float] = None
    csat_score: Optional[float] = None
    review_count: Optional[int] = None
    avg_rating: Optional[float] = None
    negative_ratio: Optional[float] = None
    response_rate: Optional[float] = None
    resolution_rate: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class BrandAlertCreate(BaseModel):
    store_id: Optional[int] = None
    alert_type: str = Field(..., max_length=50)
    severity: str = Field(..., max_length=20)
    title: str = Field(..., max_length=500)
    description: Optional[str] = None


class BrandAlertRead(BaseModel):
    id: int
    org_id: int
    store_id: Optional[int] = None
    alert_type: str
    severity: str
    title: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ExecutiveSummaryRead(BaseModel):
    org_id: int
    date: date
    brand_health: Optional[BrandHealthRead] = None
    active_alerts: int
    critical_alerts: int
    avg_sentiment: float
    review_volume: int
    top_issues: List[str]
    store_ranking: List[StoreHealthRead]
    recommended_actions: List[str]


class MetricsResponse(BaseModel):
    brand_health_trend: List[BrandHealthRead]
    store_health_current: List[StoreHealthRead]
    alert_summary: dict
    sentiment_distribution: dict
