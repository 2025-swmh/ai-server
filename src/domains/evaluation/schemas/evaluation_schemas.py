"""
Evaluation domain schemas
Clean Architecture - Interface Adapters Layer
"""
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime


class EvaluationRequest(BaseModel):
    """Request schema for evaluation"""
    session_id: str


class EvaluationResponse(BaseModel):
    """Response schema for evaluation"""
    session_id: str
    title: str
    template_type: str
    collaboration_profile: Optional[Dict[str, Any]] = None
    interview_profile: Optional[Dict[str, Any]] = None
    feedback: Dict[str, Any]
    appeal_recommendation: Dict[str, Any]


class EvaluationSummaryResponse(BaseModel):
    """Response schema for evaluation summary"""
    id: int
    session_id: str
    title: str
    interview_type: str
    created_at: datetime