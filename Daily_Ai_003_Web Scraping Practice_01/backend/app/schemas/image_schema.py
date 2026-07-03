from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.common_schema import Pagination


class ImageItem(BaseModel):
    id: int
    imageUrl: str
    imageType: Optional[str]
    createdAt: str

    class Config:
        from_attributes = True


class ImageWithArticleItem(BaseModel):
    id: int
    articleId: int
    imageUrl: str
    imageType: Optional[str]
    articleTitle: str
    articleUrl: str
    createdAt: str

    class Config:
        from_attributes = True


class ImageListResponse(BaseModel):
    items: list[ImageWithArticleItem]
    pagination: Pagination
