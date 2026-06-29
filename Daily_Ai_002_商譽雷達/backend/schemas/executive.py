from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StoreRankingItem(BaseModel):
    rank: int
    store_id: str
    store_name: str
    score: float
    nps: Optional[float] = None
    sentiment_index: float = 0.0
    alert_count: int = 0
    trend: str = "stable"
    critical_issues: int = 0


class ExecutiveRecommendation(BaseModel):
    priority: str = "medium"
    category: str
    action: str
    expected_impact: str
    expected_outcome: str = ""
    confidence: float = 0.85


class MorningBriefResponse(BaseModel):
    date: str
    summary: str
    key_metrics: Dict[str, Any]
    store_ranking: List[StoreRankingItem]
    voc_summary: str
    cx_summary: str
    risk_alerts: List[Dict[str, Any]]
    recommendations: List[ExecutiveRecommendation]
    ai_coo_analysis: Dict[str, Any] = Field(default_factory=dict)
    operational_correlations: List[Dict[str, Any]] = Field(default_factory=list)
    predictions_7day: List[Dict[str, Any]] = Field(default_factory=list)
    generated_at: datetime


class TodaySummaryResponse(BaseModel):
    date: str
    total_voices: int
    total_cases: int
    active_alerts: int
    overall_nps: Optional[float] = None
    overall_csat: Optional[float] = None
    sentiment_index: float = 0.0
    trend_direction: str = "stable"
    top_channels: List[Dict[str, Any]] = Field(default_factory=list)
    generated_at: datetime


class StoreRankingResponse(BaseModel):
    rankings: List[StoreRankingItem]
    total_stores: int
    best_performer: Optional[StoreRankingItem] = None
    worst_performer: Optional[StoreRankingItem] = None
    generated_at: datetime


class RiskSummaryResponse(BaseModel):
    total_risks: int
    by_severity: Dict[str, int]
    by_category: Dict[str, int]
    critical_alerts: List[Dict[str, Any]]
    trend: str = "stable"
    risk_score: float = 0.0
    generated_at: datetime


class KeyRiskItem(BaseModel):
    risk_id: str
    title: str
    description: str
    severity: str
    impact_score: float
    affected_stores: int
    probability: float
    financial_exposure: str
    trend_direction: str
    first_detected: str
    recommended_mitigation: str


class KeyRisksResponse(BaseModel):
    date: str
    total_active_risks: int
    overall_risk_index: float
    critical_risks: List[KeyRiskItem]
    emerging_risks: List[Dict[str, Any]]
    risk_heatmap: Dict[str, Any]
    generated_at: datetime


class OpportunityItem(BaseModel):
    opportunity_id: str
    title: str
    category: str
    potential_impact: str
    effort_required: str
    roi_estimate: str
    confidence: float
    affected_areas: List[str]
    suggested_actions: List[str]


class OpportunitiesResponse(BaseModel):
    date: str
    total_opportunities: int
    high_priority: List[OpportunityItem]
    medium_priority: List[OpportunityItem]
    quick_wins: List[OpportunityItem]
    generated_at: datetime


class AICOOSummaryItem(BaseModel):
    domain: str
    status: str
    score: float
    insights: str
    recommendations: List[str]


class AICOOSummaryResponse(BaseModel):
    date: str
    executive_statement: str
    strategic_priorities: List[Dict[str, Any]]
    domain_summaries: List[AICOOSummaryItem]
    top_actions_today: List[str]
    critical_decisions_needed: List[Dict[str, Any]]
    kpi_summary: Dict[str, Any]
    generated_at: datetime


class MetricsSnapshotResponse(BaseModel):
    timestamp: datetime
    brand_health: Dict[str, Any]
    store_health: Dict[str, Any]
    voc_metrics: Dict[str, Any]
    risk_metrics: Dict[str, Any]
    cx_metrics: Dict[str, Any]
    competitive_metrics: Dict[str, Any]
    trend_metrics: Dict[str, Any]
    generated_at: datetime
