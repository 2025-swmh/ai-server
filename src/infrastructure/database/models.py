"""
SQLAlchemy ORM models for the interview system
Clean Architecture - Frameworks & Drivers Layer
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.infrastructure.database.connection import Base


class SessionModel(Base):
    """Session model for storing interview sessions"""
    __tablename__ = "tbl_template"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    template = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversations = relationship("ConversationModel", back_populates="session")
    evaluations = relationship("EvaluationModel", back_populates="session")


class ConversationModel(Base):
    """Conversation model for storing interview dialogue"""
    __tablename__ = "tbl_conversation"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("tbl_template.session_id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("SessionModel", back_populates="conversations")


class EvaluationModel(Base):
    """Evaluation model for storing interview assessments"""
    __tablename__ = "tbl_evaluation"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), ForeignKey("tbl_template.session_id"), nullable=False)
    evaluation_json = Column(Text, nullable=False)  # JSON string - matches existing table
    title = Column(String(255), nullable=True)
    interview_type = Column(String(50), nullable=True)
    type_korean = Column(String(100), nullable=True)
    type_english = Column(String(100), nullable=True)
    score_relationship = Column(String(10), nullable=True)
    score_problem = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("SessionModel", back_populates="evaluations")