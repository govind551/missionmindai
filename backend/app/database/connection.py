from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.logging import logger
from app.database.base import Base

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
elif "postgresql" in settings.DATABASE_URL:
    connect_args = {"connect_timeout": 2}

try:
    engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
    # Fast test connection
    with engine.connect() as conn:
        if "postgresql" in settings.DATABASE_URL:
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()
                logger.info("PostgreSQL pgvector extension verified/enabled.")
            except Exception as e:
                logger.warning(f"Could not enable pgvector extension: {e}")
        logger.info(f"Connected to database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
except Exception as e:
    logger.warning(f"Primary database connection failed ({e}). Falling back to local SQLite.")
    sqlite_url = "sqlite:///./missionmind.db"
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    import app.models  # noqa
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized.")
