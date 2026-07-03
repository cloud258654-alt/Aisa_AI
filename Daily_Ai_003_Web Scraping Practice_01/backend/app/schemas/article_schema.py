from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.common_schema import Pagination
from app.schemas.image_schema import ImageItem


class ArticleItem(BaseModel):
    id: int
    title: str
    author: Optional[str]
    articleUrl: str
    articleDate: Optional[str]
    pushCount: int
    sourceBoard: str
    imageCount: int
    createdAt: str

    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    items: list[ArticleItem]
    pagination: Pagination


class ArticleDetailResponse(BaseModel):
    id: int
    title: str
    author: Optional[str]
    articleUrl: str
    articleDate: Optional[str]
    pushCount: int
    sourceBoard: str
    images: list[ImageItem]
    createdAt: str
    updatedAt: str
