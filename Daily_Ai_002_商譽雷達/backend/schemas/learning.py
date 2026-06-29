from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LearningCaseCreate(BaseModel):
    case_title: str = Field(..., min_length=1, max_length=500)
    case_description: str
    event_type: str
    store_id: Optional[int] = None
    resolution_action: str
    resolution_outcome: str
    success_rating: int = Field(default=3, ge=1, le=5)
    tags: Optional[List[str]] = None


class LearningCaseRead(BaseModel):
    id: int
    org_id: int
    case_title: str
    case_description: str
    event_type: str
    store_id: Optional[int] = None
    store_name: Optional[str] = None
    resolution_action: str
    resolution_outcome: str
    success_rating: int
    tags: Optional[List[str]] = None
    similar_case_ids: Optional[List[int]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class LearningCaseList(BaseModel):
    items: List[LearningCaseRead]
    total: int
    page: int
    page_size: int
    total_pages: int


class SimilarCaseItem(BaseModel):
    case: LearningCaseRead
    similarity_score: float
    matching_keywords: List[str]


class SimilarCaseResponse(BaseModel):
    query_case: Optional[LearningCaseRead] = None
    similar_cases: List[SimilarCaseItem]
    query_text: Optional[str] = None


class LearningPatternRead(BaseModel):
    id: int
    org_id: int
    pattern_name: str
    pattern_description: str
    event_type: str
    frequency: int
    success_rate: float
    recommended_actions: Optional[List[str]] = None
    last_updated_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class LearningPatternList(BaseModel):
    items: List[LearningPatternRead]
    total: int


class PatternDiscoveryResponse(BaseModel):
    patterns: List[LearningPatternRead]
    total_cases_analyzed: int
    discovery_method: str


class RecommendationOutcomeCreate(BaseModel):
    case_id: int
    recommendation_id: Optional[int] = None
    action_taken: str
    outcome: str
    effectiveness_score: int = Field(default=3, ge=1, le=5)
    feedback_notes: Optional[str] = None


class RecommendationOutcomeRead(BaseModel):
    id: int
    org_id: int
    recommendation_id: Optional[int] = None
    case_id: int
    action_taken: str
    outcome: str
    effectiveness_score: int
    feedback_notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RecommendationHistoryItem(BaseModel):
    event_type: str
    action_taken: str
    outcome: str
    effectiveness_score: int
    case_title: Optional[str] = None
    created_at: datetime


class RecommendationHistoryResponse(BaseModel):
    recommendations: List[RecommendationHistoryItem]
    event_type: Optional[str] = None
    total: int


class SimilarCasesQuery(BaseModel):
    query_text: str
    limit: int = Field(default=5, ge=1, le=20)


class ImproveRecommendationsResponse(BaseModel):
    patterns_updated: int
    cases_improved: int
    message: str
