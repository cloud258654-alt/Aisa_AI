from sqlalchemy.orm import Session

from app.repositories import image_repository
from app.repositories.article_repository import get_article_by_id


def get_image_list(
    db: Session, page: int, page_size: int, article_id: int | None = None
) -> dict:
    skip = (page - 1) * page_size

    items = image_repository.list_images(
        db, skip=skip, limit=page_size, article_id=article_id
    )

    if article_id is not None:
        total = image_repository.count_images_by_article(db, article_id)
    else:
        total = image_repository.count_images(db)

    total_pages = max(1, (total + page_size - 1) // page_size)

    result_items = []
    for img in items:
        article = get_article_by_id(db, img.article_id)
        result_items.append(
            {
                "id": img.id,
                "articleId": img.article_id,
                "imageUrl": img.image_url,
                "imageType": img.image_type,
                "articleTitle": article.title if article else "",
                "articleUrl": article.article_url if article else "",
                "createdAt": _fmt_dt(img.created_at),
            }
        )

    return {
        "items": result_items,
        "pagination": {
            "page": page,
            "pageSize": page_size,
            "total": total,
            "totalPages": total_pages,
        },
    }


def _fmt_dt(dt) -> str:
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%dT%H:%M:%S") if hasattr(dt, "strftime") else str(dt)
