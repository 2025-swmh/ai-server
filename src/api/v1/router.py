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
from src.domains.session.schemas import (
    SessionCreateRequest,
    SessionResponse,
    HealthResponse
)

api_router = APIRouter()


@api_router.post("/session/template")
async def save_session_template(
    request: SessionCreateRequest,
    db: Session = Depends(get_db)
):
    """Save or update session template"""
    try:
        # Check if session already exists
        existing_session = session_service.get_session_by_id(request.session_id, db)
        if existing_session:
            # Update existing session template
            session_service.create_session(
                session_id=request.session_id,
                template=request.template,
                db=db
            )
            return {"message": "템플릿이 정상적으로 업데이트되었습니다."}
        else:
            # Create new session
            session_service.create_session(
                session_id=request.session_id,
                template=request.template,
                db=db
            )
            return {"message": "템플릿이 정상적으로 저장되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")


@api_router.post("/question/start", response_model=QuestionStartResponse)
async def question_start(
    request: QuestionStartRequest,
    db: Session = Depends(get_db)
):
    """Start a new interview question session"""
    try:
        # Check if session exists with template
        existing_session = session_service.get_session_by_id(request.session_id, db)
        if not existing_session:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다. 먼저 템플릿을 설정해주세요.")
        
        # If scenario is provided, only cooperation template is allowed
        if request.scenario and existing_session.template != "cooperation":
            raise HTTPException(
                status_code=400, 
                detail="시나리오 기반 면접은 cooperation 템플릿에서만 가능합니다."
            )
        
        result = await question_service.generate_first_question(
            session_id=request.session_id,
            db=db,
            scenario=request.scenario
        )
        return result
    except HTTPException:
        raise
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