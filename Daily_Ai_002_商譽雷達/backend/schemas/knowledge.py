from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=256)
    content: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1, max_length=128)
    tags: List[str] = Field(default_factory=list)
    is_published: bool = False
    source_voice_id: Optional[str] = None
    source_case_id: Optional[str] = None


class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=256)
    content: Optional[str] = None
    category: Optional[str] = Field(None, min_length=1, max_length=128)
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None


class ArticleResponse(BaseModel):
    id: str
    title: str
    content: str
    category: str
    tags: List[str] = Field(default_factory=list)
    is_published: bool = False
    version: int = 1
    author: Optional[str] = None
    source_voice_id: Optional[str] = None
    source_case_id: Optional[str] = None
    view_count: int = 0
    created_at: datetime
    updated_at: datetime


class ArticleSearchResult(BaseModel):
    id: str
    title: str
    category: str
    snippet: str
    relevance_score: float
    tags: List[str] = Field(default_factory=list)
    updated_at: datetime


class ArticleSearchResponse(BaseModel):
    query: str
    results: List[ArticleSearchResult] = Field(default_factory=list)
    total_results: int = 0
    search_time_ms: Optional[float] = None
