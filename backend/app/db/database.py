from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from app.config import get_settings

settings = get_settings()

# psycopg3 SQLAlchemy URL
_url = settings.database_url.replace("postgresql://", "postgresql+psycopg://", 1)
engine = create_engine(_url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    schema_path = Path(__file__).parent / "schema.sql"
    schema = schema_path.read_text(encoding="utf-8")
    with engine.begin() as conn:
        for stmt in [s.strip() for s in schema.split(";") if s.strip()]:
            conn.execute(text(stmt))


def get_session() -> Session:
    db = SessionLocal()
    try:
        return db
    finally:
        pass
