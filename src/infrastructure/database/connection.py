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

# Database configuration with fallback for AWS RDS
DB_USER = os.getenv("DB_USER", "tmp")
DB_PASSWORD = os.getenv("DB_PASSWORD", "tmp")
DB_HOST = os.getenv("DB_HOST", "tmp")
DB_PORT = os.getenv("DB_PORT", "tmp")
DB_NAME = os.getenv("DB_NAME", "tmp")

# Use environment-specific database URL
if all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    DATABASE_URL = settings.DATABASE_URL

# Database engine with production-ready configuration
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,        # Verify connections before use
    pool_size=10,              # Connection pool size
    max_overflow=20,           # Additional connections beyond pool_size
    pool_recycle=3600,         # Recycle connections every hour
    echo=settings.DEBUG        # SQL logging in debug mode
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Declarative base for ORM models
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