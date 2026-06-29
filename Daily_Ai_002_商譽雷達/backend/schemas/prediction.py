from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# PredictionResult
# ---------------------------------------------------------------------------
class PredictionResultRead(BaseModel):
    id: int
    org_id: int
    store_id: Optional[int] = None
    prediction_type: str
    target_date: date
    predicted_value: float
    confidence_lower: Optional[float] = None
    confidence_upper: Optional[float] = None
    model_version: Optional[str] = None
    features_used: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PredictionResultList(BaseModel):
    items: List[PredictionResultRead]
    total: int
    page: int
    page_size: int


# ---------------------------------------------------------------------------
# Forecast
# ---------------------------------------------------------------------------
class ForecastPoint(BaseModel):
    date: date
    value: float
    lower_bound: float
    upper_bound: float


class PredictionForecastResponse(BaseModel):
    prediction_type: str
    forecasts: List[ForecastPoint] = Field(default_factory=list)
    trend_direction: str = Field(default="stable", pattern="^(improving|stable|declining)$")
    confidence: float = Field(default=0.0, ge=0, le=1)
    methodology: str = "weighted_moving_average_trend"


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------
class SimulateRequest(BaseModel):
    scenario_description: str = Field(..., min_length=3)
    variables: Dict[str, float] = Field(..., description="Metric name -> change value")
    store_id: Optional[int] = None


class SimulateResponse(BaseModel):
    scenario: str
    baseline_value: float
    simulated_value: float
    impact_assessment: str
    confidence: float = Field(default=0.0, ge=0, le=1)
