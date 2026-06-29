from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CompetitorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_active: bool = True


class CompetitorResponse(BaseModel):
    id: str
    name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class MetricComparison(BaseModel):
    metric_name: str
    our_value: float
    competitor_value: float
    industry_avg: Optional[float] = None
    difference: float
    trend: str = "stable"


class CompetitorMetricsResponse(BaseModel):
    competitor_id: str
    competitor_name: str
    metrics: List[MetricComparison] = Field(default_factory=list)
    overall_position: str = "neutral"
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    measured_at: datetime


class BenchmarkDataPoint(BaseModel):
    metric_name: str
    our_score: float
    competitor_avg: float
    top_performer: float
    industry_benchmark: Optional[float] = None
    percentile: Optional[float] = None


class BenchmarkResponse(BaseModel):
    benchmarks: List[BenchmarkDataPoint] = Field(default_factory=list)
    overall_rank: Optional[int] = None
    total_competitors: int = 0
    strengths_against_competitors: List[str] = Field(default_factory=list)
    weaknesses_against_competitors: List[str] = Field(default_factory=list)
    generated_at: datetime


class SWOTItem(BaseModel):
    category: str  # strength, weakness, opportunity, threat
    description: str
    impact_score: float = 0.0
    evidence: Optional[str] = None


class SWOTResponse(BaseModel):
    competitor_id: str
    competitor_name: str
    strengths: List[SWOTItem] = Field(default_factory=list)
    weaknesses: List[SWOTItem] = Field(default_factory=list)
    opportunities: List[SWOTItem] = Field(default_factory=list)
    threats: List[SWOTItem] = Field(default_factory=list)
    overall_assessment: Optional[str] = None
    generated_at: datetime
