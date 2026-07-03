from sqlalchemy.orm import Session

from app.repositories import article_repository, image_repository


def get_article_list(
    db: Session, page: int, page_size: int, sort_by: str, order: str
) -> dict:
    sort_prefix = "" if order == "asc" else "-"
    sort_key = f"{sort_prefix}{sort_by}"
    skip = (page - 1) * page_size

    items = article_repository.list_articles(
        db, skip=skip, limit=page_size, sort=sort_key
    )
    total = article_repository.count_articles(db)
    total_pages = max(1, (total + page_size - 1) // page_size)

    result_items = []
    for article in items:
        image_count = image_repository.count_images_by_article(db, article.id)
        result_items.append(_article_to_item(article, image_count))

    return {
        "items": result_items,
        "pagination": {
            "page": page,
            "pageSize": page_size,
            "total": total,
            "totalPages": total_pages,
        },
    }


def get_article_detail(db: Session, article_id: int):
    article = article_repository.get_article_by_id(db, article_id)
    if not article:
        return None

    images = image_repository.list_images(db, article_id=article_id, limit=100)

    return {
        "id": article.id,
        "title": article.title,
        "author": article.author,
        "articleUrl": article.article_url,
        "articleDate": _fmt_date(article.article_date),
        "pushCount": article.push_count,
        "sourceBoard": article.source_board,
        "images": [
            {
                "id": img.id,
                "imageUrl": img.image_url,
                "imageType": img.image_type,
                "createdAt": _fmt_dt(img.created_at),
            }
            for img in images
        ],
        "createdAt": _fmt_dt(article.created_at),
        "updatedAt": _fmt_dt(article.updated_at),
    }


def _article_to_item(article, image_count: int) -> dict:
    return {
        "id": article.id,
        "title": article.title,
        "author": article.author,
        "articleUrl": article.article_url,
        "articleDate": _fmt_date(article.article_date),
        "pushCount": article.push_count,
        "sourceBoard": article.source_board,
        "imageCount": image_count,
        "createdAt": _fmt_dt(article.created_at),
    }


def _fmt_date(dt) -> str | None:
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d") if hasattr(dt, "strftime") else str(dt)[:10]


def _fmt_dt(dt) -> str:
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%dT%H:%M:%S") if hasattr(dt, "strftime") else str(dt)
