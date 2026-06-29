from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class CaseCreate(BaseModel):
    store_id: Optional[int] = None
    voice_source_id: Optional[int] = None
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    status: str = Field("new", max_length=20)
    priority: str = Field("medium", max_length=20)
    assigned_to: Optional[int] = None


class CaseUpdate(BaseModel):
    store_id: Optional[int] = None
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    status: Optional[str] = Field(None, max_length=20)
    priority: Optional[str] = Field(None, max_length=20)
    assigned_to: Optional[int] = None


class CaseRead(BaseModel):
    id: int
    org_id: int
    store_id: Optional[int] = None
    voice_source_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    assigned_to: Optional[int] = None
    created_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    timeline: List["CaseTimelineRead"] = []

    model_config = {"from_attributes": True}


class CaseTimelineRead(BaseModel):
    id: int
    case_id: int
    action: str
    comment: Optional[str] = None
    performed_by: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}
