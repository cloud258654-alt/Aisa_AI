from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

DB_DIR = Path(__file__).resolve().parent.parent.parent / "database"
DB_PATH = DB_DIR / "memes.db"

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)


class Base(DeclarativeBase):
    pass
