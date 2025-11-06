"""
Session domain schemas
Clean Architecture - Interface Adapters Layer
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SessionCreateRequest(BaseModel):
    """Request schema for creating session"""
    session_id: str
    template: str


class SessionResponse(BaseModel):
    """Response schema for session"""
    id: int
    session_id: str
    template: str
    created_at: datetime


class SessionListResponse(BaseModel):
    """Response schema for session list"""
    sessions: list[SessionResponse]
    total: int


class HealthResponse(BaseModel):
    """Response schema for health check"""
    status: str
    timestamp: str
    service: Optional[str] = None
    version: Optional[str] = None