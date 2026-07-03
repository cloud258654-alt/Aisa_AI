from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.search_service import search_articles

router = APIRouter(tags=["search"])

MAX_PAGE_SIZE = 100


@router.get("/search")
def search(
    q: str | None = Query(None),
    page: int = Query(1),
    pageSize: int = Query(20),
    db: Session = Depends(get_db),
):
    if not q:
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "MISSING_QUERY",
                    "message": "Query parameter 'q' is required",
                }
            },
        )
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
    result = search_articles(db, q, page, page_size)
    return result
