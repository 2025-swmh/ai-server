"""
Interview domain schemas
Clean Architecture - Interface Adapters Layer
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class QuestionStartRequest(BaseModel):
    """Request schema for starting interview questions"""
    session_id: str
    scenario: Optional[str] = None


class AnswerRequest(BaseModel):
    """Request schema for user answers"""
    session_id: str
    message: str


class QuestionStartResponse(BaseModel):
    """Response schema for question start"""
    message: str
    session_id: str
    template_id: str
    timestamp: str


class AnswerResponse(BaseModel):
    """Response schema for AI answers"""
    message: str
    session_id: str
    template_id: str
    timestamp: str


class ConversationResponse(BaseModel):
    """Response schema for conversation"""
    id: int
    session_id: str
    role: str
    content: str
    created_at: datetime