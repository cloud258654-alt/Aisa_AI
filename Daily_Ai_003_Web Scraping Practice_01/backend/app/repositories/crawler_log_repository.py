from sqlalchemy.orm import Session

from app.models.crawler_log import CrawlerLog


def create_crawler_log(db: Session, **kwargs) -> CrawlerLog:
    log = CrawlerLog(**kwargs)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_latest_crawler_log(db: Session) -> CrawlerLog | None:
    return db.query(CrawlerLog).order_by(CrawlerLog.created_at.desc()).first()


def count_crawler_logs(db: Session) -> int:
    return db.query(CrawlerLog).count()
