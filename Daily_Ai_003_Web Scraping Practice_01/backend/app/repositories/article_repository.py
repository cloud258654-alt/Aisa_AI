from sqlalchemy.orm import Session

from app.models.article import Article


def create_article(db: Session, **kwargs) -> Article:
    article = Article(**kwargs)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def get_article_by_id(db: Session, article_id: int) -> Article | None:
    return db.query(Article).filter(Article.id == article_id).first()


def get_article_by_url(db: Session, article_url: str) -> Article | None:
    return db.query(Article).filter(Article.article_url == article_url).first()


def list_articles(
    db: Session, skip: int = 0, limit: int = 20, sort: str = "-article_date"
) -> list[Article]:
    query = db.query(Article)
    if sort.startswith("-"):
        column = getattr(Article, sort[1:])
        query = query.order_by(column.desc())
    else:
        column = getattr(Article, sort)
        query = query.order_by(column.asc())
    return query.offset(skip).limit(limit).all()


def count_articles(db: Session) -> int:
    return db.query(Article).count()


def search_articles(
    db: Session, q: str, skip: int = 0, limit: int = 20
) -> list[Article]:
    pattern = f"%{q}%"
    return (
        db.query(Article)
        .filter(
            Article.title.ilike(pattern) | Article.author.ilike(pattern)
        )
        .order_by(Article.article_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def count_articles_search(db: Session, q: str) -> int:
    pattern = f"%{q}%"
    return (
        db.query(Article)
        .filter(
            Article.title.ilike(pattern) | Article.author.ilike(pattern)
        )
        .count()
    )


def list_popular_articles(
    db: Session, skip: int = 0, limit: int = 20
) -> list[Article]:
    return (
        db.query(Article)
        .order_by(Article.push_count.desc(), Article.article_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
