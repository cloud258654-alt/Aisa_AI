from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class SandboxAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    channel: Optional[str] = Field(None, max_length=30)
    language: str = Field("zh", max_length=10)
    analyze_sentiment: bool = True
    analyze_emotion: bool = True
    analyze_intent: bool = True
    analyze_risk: bool = True
    detect_needs: bool = True


class SandboxSentiment(BaseModel):
    sentiment: str
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    confidence: float = Field(..., ge=0, le=1.0)


class SandboxRecommendation(BaseModel):
    action: str
    priority: str
    rationale: Optional[str] = None


class SandboxAnalyzeResponse(BaseModel):
    request_id: str
    original_text: str
    sentiment: SandboxSentiment
    emotion: Optional[str] = None
    intent: Optional[str] = None
    risk_level: Optional[str] = None
    risk_score: Optional[int] = Field(None, ge=0, le=100)
    pain_point_score: Optional[float] = Field(None, ge=0, le=10)
    needs_detected: List[str] = []
    recommendations: List[SandboxRecommendation] = []
    analyzed_at: datetime
