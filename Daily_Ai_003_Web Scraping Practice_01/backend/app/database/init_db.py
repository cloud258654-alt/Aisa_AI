from app.database.database import DB_DIR, Base, engine


def init_db():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    import app.models.article
    import app.models.image
    import app.models.crawler_log

    Base.metadata.create_all(bind=engine)
