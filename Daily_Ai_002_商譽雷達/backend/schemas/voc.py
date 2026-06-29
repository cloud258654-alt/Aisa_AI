from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class VoiceSourceCreate(BaseModel):
    store_id: Optional[int] = None
    channel: str = Field(..., max_length=30)
    source_url: Optional[str] = None
    author_name: Optional[str] = Field(None, max_length=255)
    content: str
    rating: Optional[float] = Field(None, ge=0, le=5)
    posted_at: Optional[datetime] = None


class VoiceSourceRead(BaseModel):
    id: int
    org_id: int
    store_id: Optional[int] = None
    channel: str
    source_url: Optional[str] = None
    author_name: Optional[str] = None
    content: str
    rating: Optional[float] = None
    posted_at: Optional[datetime] = None
    fetched_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class VoiceSourceList(BaseModel):
    items: List[VoiceSourceRead]
    total: int
    page: int
    page_size: int


class VoiceAnalysisCreate(BaseModel):
    voice_source_id: int
    sentiment: str = Field(..., max_length=20)
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    emotion: Optional[str] = Field(None, max_length=50)
    topic: Optional[str] = Field(None, max_length=100)
    journey_touchpoint: Optional[str] = Field(None, max_length=50)
    pain_point_score: Optional[float] = Field(None, ge=0, le=10)
    intent: Optional[str] = Field(None, max_length=50)
    need_detected: Optional[str] = None
    risk_level: Optional[str] = Field(None, max_length=20)
    risk_score: Optional[int] = Field(None, ge=0, le=100)


class VoiceAnalysisRead(BaseModel):
    id: int
    voice_source_id: int
    sentiment: str
    sentiment_score: float
    emotion: Optional[str] = None
    topic: Optional[str] = None
    journey_touchpoint: Optional[str] = None
    pain_point_score: Optional[float] = None
    intent: Optional[str] = None
    need_detected: Optional[str] = None
    risk_level: Optional[str] = None
    risk_score: Optional[int] = None
    analyzed_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class VoiceStreamItem(BaseModel):
    source_id: int
    channel: str
    author_name: Optional[str] = None
    content: str
    rating: Optional[float] = None
    sentiment: Optional[str] = None
    risk_level: Optional[str] = None
    posted_at: Optional[datetime] = None
