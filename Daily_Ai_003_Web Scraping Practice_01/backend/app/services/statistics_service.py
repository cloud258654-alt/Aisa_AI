from sqlalchemy.orm import Session

from app.repositories import article_repository, crawler_log_repository, image_repository


def get_statistics(db: Session) -> dict:
    articles_count = article_repository.count_articles(db)
    images_count = image_repository.count_images(db)
    logs_count = crawler_log_repository.count_crawler_logs(db)
    latest_log = crawler_log_repository.get_latest_crawler_log(db)

    return {
        "articles": articles_count,
        "images": images_count,
        "crawlerLogs": logs_count,
        "lastCrawlerStatus": latest_log.status if latest_log else None,
        "lastUpdate": latest_log.created_at.isoformat() if latest_log else None,
    }
