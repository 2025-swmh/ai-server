"""
Main API router for version 1
Clean Architecture - Interface Adapters Layer
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

# Import domain services
from src.domains.interview.services.question_service import question_service
from src.domains.evaluation.services.evaluation_service import evaluation_service
from src.domains.session.services.session_service import session_service
from src.infrastructure.database.connection import get_db

# Import schemas
from src.domains.interview.schemas import (
    QuestionStartRequest, 
    AnswerRequest,
    QuestionStartResponse
)
from src.domains.evaluation.schemas import EvaluationRequest
from src.domains.session.schemas import HealthResponse

api_router = APIRouter()


@api_router.post("/question/start", response_model=QuestionStartResponse)
async def question_start(
    request: QuestionStartRequest,
    db: Session = Depends(get_db)
):
    """Start a new interview question session"""
    try:
        # Ensure session exists
        session_service.create_session(
            session_id=request.session_id,
            template="cooperation",  # Default template, can be made configurable
            db=db
        )
        
        result = await question_service.generate_first_question(
            session_id=request.session_id,
            db=db,
            scenario=request.scenario
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@api_router.post("/question/answer")
async def question_answer(
    request: AnswerRequest,
    db: Session = Depends(get_db)
):
    """Process user answer and generate AI response"""
    try:
        result = await question_service.generate_response(
            session_id=request.session_id,
            user_message=request.message,
            db=db
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@api_router.post("/evaluation")
async def evaluate_interview(
    request: EvaluationRequest,
    db: Session = Depends(get_db)
):
    """Generate interview evaluation"""
    try:
        result = await evaluation_service.generate_evaluation(
            session_id=request.session_id,
            db=db
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@api_router.get("/health", response_model=HealthResponse)
async def api_health():
    """API v1 health check"""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now().isoformat(),
        service="AI Interview System",
        version="1.0.0"
    )