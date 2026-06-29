from enum import Enum
from typing import Generic, TypeVar, Optional, List, Any

from pydantic import BaseModel, Field


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class FilterParams(BaseModel):
    q: Optional[str] = Field(None, description="Search query string")
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: SortOrder = Field(SortOrder.desc, description="Sort direction")


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    errors: Optional[List[dict]] = None


class SuccessResponse(BaseModel):
    message: str
    data: Optional[Any] = None
