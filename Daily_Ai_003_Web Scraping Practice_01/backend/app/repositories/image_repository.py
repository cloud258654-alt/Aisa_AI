from sqlalchemy.orm import Session

from app.models.image import Image


def create_image(db: Session, **kwargs) -> Image:
    image = Image(**kwargs)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


def get_image_by_url(db: Session, image_url: str) -> Image | None:
    return db.query(Image).filter(Image.image_url == image_url).first()


def list_images(
    db: Session, skip: int = 0, limit: int = 20, article_id: int | None = None
) -> list[Image]:
    query = db.query(Image)
    if article_id is not None:
        query = query.filter(Image.article_id == article_id)
    return query.offset(skip).limit(limit).all()


def count_images(db: Session) -> int:
    return db.query(Image).count()


def count_images_by_article(db: Session, article_id: int) -> int:
    return db.query(Image).filter(Image.article_id == article_id).count()
