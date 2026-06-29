from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TrendPeriodData(BaseModel):
    period: str
    total_voices: int
    sentiment_index: float
    avg_sentiment: float
    positive_pct: float
    neutral_pct: float
    negative_pct: float
    change_from_previous: Optional[float] = None


class TrendOverviewResponse(BaseModel):
    current_7d: TrendPeriodData
    current_30d: TrendPeriodData
    current_90d: TrendPeriodData
    current_1y: TrendPeriodData
    generated_at: datetime


class TopTopic(BaseModel):
    topic: str
    count: int
    sentiment_trend: str = "stable"
    growth_rate: Optional[float] = None
    related_keywords: List[str] = Field(default_factory=list)
    sample_voices: List[str] = Field(default_factory=list)


class TopicResponse(BaseModel):
    topics: List[TopTopic] = Field(default_factory=list)
    total_topics_analyzed: int
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    generated_at: datetime


class EmotionDataPoint(BaseModel):
    date: str
    joy: float = 0.0
    sadness: float = 0.0
    anger: float = 0.0
    fear: float = 0.0
    surprise: float = 0.0
    disgust: float = 0.0
    trust: float = 0.0
    anticipation: float = 0.0
    dominant_emotion: str = "neutral"


class EmotionResponse(BaseModel):
    time_series: List[EmotionDataPoint] = Field(default_factory=list)
    period_summary: Dict[str, float] = Field(default_factory=dict)
    generated_at: datetime


class WeeklyPrediction(BaseModel):
    week_start: str
    predicted_volume: int
    predicted_sentiment: float
    risk_level: str = "low"
    top_predicted_topics: List[str] = Field(default_factory=list)
    confidence: float = 0.0


class PredictionResponse(BaseModel):
    predictions: List[WeeklyPrediction] = Field(default_factory=list)
    model_version: Optional[str] = None
    forecast_weeks: int = 4
    overall_confidence: float = 0.0
    generated_at: datetime
