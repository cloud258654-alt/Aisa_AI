from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.article_service import get_article_detail, get_article_list

router = APIRouter(tags=["articles"])

ALLOWED_SORT = {"article_date", "push_count", "created_at"}
ALLOWED_ORDER = {"asc", "desc"}
MAX_PAGE_SIZE = 100


def _validate_page(page: int, pageSize: int):
    if page < 1:
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "INVALID_PAGE",
                    "message": f"Page must be >= 1, got {page}",
                }
            },
        )
    if pageSize < 1:
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "INVALID_PAGE_SIZE",
                    "message": f"PageSize must be >= 1, got {pageSize}",
                }
            },
        )
    return None


@router.get("/articles")
def list_articles(
    page: int = Query(1),
    pageSize: int = Query(20),
    sortBy: str = Query("article_date"),
    order: str = Query("desc"),
    db: Session = Depends(get_db),
):
    err = _validate_page(page, pageSize)
    if err:
        return err

    if sortBy not in ALLOWED_SORT:
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "INVALID_SORT",
                    "message": f"Invalid sortBy: {sortBy}. Allowed: {', '.join(sorted(ALLOWED_SORT))}",
                }
            },
        )
    if order not in ALLOWED_ORDER:
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "INVALID_SORT",
                    "message": f"Invalid order: {order}. Allowed: {', '.join(sorted(ALLOWED_ORDER))}",
                }
            },
        )

    page_size = min(pageSize, MAX_PAGE_SIZE)
    result = get_article_list(db, page, page_size, sortBy, order)
    return result


@router.get("/articles/{article_id}")
def get_article(article_id: int, db: Session = Depends(get_db)):
    result = get_article_detail(db, article_id)
    if result is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Article {article_id} not found",
                }
            },
        )
    return result
