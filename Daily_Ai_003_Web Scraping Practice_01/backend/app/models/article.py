from sqlalchemy import Column, DateTime, Index, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=True)
    article_url = Column(String, nullable=False, unique=True)
    article_date = Column(DateTime, nullable=True)
    push_count = Column(Integer, default=0)
    source_board = Column(String, default="joke")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    images = relationship("Image", back_populates="article", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_articles_article_date", "article_date"),
        Index("ix_articles_push_count", "push_count"),
        Index("ix_articles_author", "author"),
    )

    def __repr__(self):
        return f"<Article(id={self.id}, title={self.title!r})>"
