from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.image_service import get_image_list

router = APIRouter(tags=["images"])

MAX_PAGE_SIZE = 100


@router.get("/images")
def list_images(
    page: int = Query(1),
    pageSize: int = Query(30),
    articleId: int | None = Query(None),
    db: Session = Depends(get_db),
):
    if page < 1:
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "INVALID_PAGE", "message": f"Page must be >= 1, got {page}"}},
        )
    if pageSize < 1:
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "INVALID_PAGE_SIZE", "message": f"PageSize must be >= 1, got {pageSize}"}},
        )

    page_size = min(pageSize, MAX_PAGE_SIZE)
    result = get_image_list(db, page, page_size, article_id=articleId)
    return result
