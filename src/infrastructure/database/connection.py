"""
Database connection and session management
Clean Architecture - Frameworks & Drivers Layer
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from dotenv import load_dotenv
from src.core.config.settings import settings

load_dotenv()

DB_USER = os.getenv("DB_USER", "tmp")
DB_PASSWORD = os.getenv("DB_PASSWORD", "tmp")
DB_HOST = os.getenv("DB_HOST", "tmp")
DB_PORT = os.getenv("DB_PORT", "tmp")
DB_NAME = os.getenv("DB_NAME", "tmp")

if all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI
    
    Yields:
        Session: SQLAlchemy session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)