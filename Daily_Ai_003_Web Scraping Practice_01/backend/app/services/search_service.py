from sqlalchemy.orm import Session

from app.repositories import article_repository, image_repository
from app.services.article_service import _article_to_item


def search_articles(
    db: Session, q: str, page: int, page_size: int
) -> dict:
    skip = (page - 1) * page_size
    items = article_repository.search_articles(db, q=q, skip=skip, limit=page_size)
    total = article_repository.count_articles_search(db, q=q)
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


def get_popular_articles(
    db: Session, page: int, page_size: int
) -> dict:
    skip = (page - 1) * page_size
    items = article_repository.list_popular_articles(
        db, skip=skip, limit=page_size
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
