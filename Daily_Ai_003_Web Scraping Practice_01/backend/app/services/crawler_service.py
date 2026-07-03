import logging
from datetime import datetime, timezone

from app.crawler.ptt_joke_crawler import crawl_joke_board
from app.database.database import DB_DIR
from app.database.init_db import init_db
from app.database.session import SessionLocal
from app.repositories import article_repository, crawler_log_repository, image_repository

logger = logging.getLogger("crawler")


def run_crawler(pages: int = 1, delay: int = 2) -> dict:
    init_db()
    log = None
    new_articles = 0
    new_images = 0
    error_msg = None
    status = "success"

    db = SessionLocal()
    try:
        log = crawler_log_repository.create_crawler_log(
            db,
            crawler_name="ptt_joke",
            start_time=datetime.now(timezone.utc),
            status="running",
        )

        articles = crawl_joke_board(pages=pages, delay=delay)

        for art in articles:
            existing = article_repository.get_article_by_url(db, art["article_url"])
            if existing:
                logger.info("Skipping duplicate article: %s", art["article_url"])
                continue

            article = article_repository.create_article(
                db,
                title=art["title"],
                author=art.get("author"),
                article_url=art["article_url"],
                article_date=art.get("article_date"),
                push_count=art.get("push_count", 0),
                source_board="joke",
            )
            new_articles += 1

            for img_url in art.get("images", []):
                existing_img = image_repository.get_image_by_url(db, img_url)
                if existing_img:
                    logger.info("Skipping duplicate image: %s", img_url)
                    continue

                image_type = _guess_image_type(img_url)
                image_repository.create_image(
                    db,
                    article_id=article.id,
                    image_url=img_url,
                    image_type=image_type,
                )
                new_images += 1

        status = "success"

    except Exception as e:
        logger.exception("Crawler failed: %s", e)
        status = "failed"
        error_msg = str(e)

    finally:
        if log:
            log.end_time = datetime.now(timezone.utc)
            log.status = status
            log.new_articles = new_articles
            log.new_images = new_images
            log.error_message = error_msg
            db.commit()
        db.close()

    return {
        "status": status,
        "new_articles": new_articles,
        "new_images": new_images,
        "error_message": error_msg,
    }


def _guess_image_type(url: str) -> str:
    from urllib.parse import urlparse

    parsed = urlparse(url)
    path = parsed.path.lower()
    if path.endswith(".jpg") or path.endswith(".jpeg"):
        return "jpg"
    if path.endswith(".png"):
        return "png"
    if path.endswith(".gif"):
        return "gif"
    if path.endswith(".webp"):
        return "webp"
    if "imgur" in parsed.netloc:
        return "imgur"
    return "unknown"
