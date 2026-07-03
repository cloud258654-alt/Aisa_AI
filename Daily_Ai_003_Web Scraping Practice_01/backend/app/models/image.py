from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    image_url = Column(String, nullable=False, unique=True)
    image_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())

    article = relationship("Article", back_populates="images")

    def __repr__(self):
        return f"<Image(id={self.id}, url={self.image_url!r})>"
