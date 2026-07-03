from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.search_service import get_popular_articles

router = APIRouter(tags=["popular"])

MAX_PAGE_SIZE = 100


@router.get("/popular")
def popular(
    page: int = Query(1),
    pageSize: int = Query(20),
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
    result = get_popular_articles(db, page, page_size)
    return result
