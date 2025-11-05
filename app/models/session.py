from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base


class Session(Base):
    __tablename__ = "tbl_session"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    template = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
