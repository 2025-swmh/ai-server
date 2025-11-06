"""
Session management service
Clean Architecture - Application Business Rules Layer
"""
from typing import Optional
from sqlalchemy.orm import Session as DBSession
from datetime import datetime

from src.domains.session.models.session import Session
from src.infrastructure.database.models import SessionModel
from src.core.exceptions.handlers import SessionNotFoundException


class SessionService:
    """Service for managing interview sessions"""

    @staticmethod
    def create_session(session_id: str, template: str, db: DBSession) -> Session:
        """Create a new interview session"""
        
        # Check if session already exists
        existing = db.query(SessionModel).filter(
            SessionModel.session_id == session_id
        ).first()
        
        if existing:
            # Update existing session
            existing.template = template
            db.commit()
            db.refresh(existing)
            return Session(
                id=existing.id,
                session_id=existing.session_id,
                template=existing.template,
                created_at=existing.created_at
            )
        else:
            # Create new session
            session_model = SessionModel(
                session_id=session_id,
                template=template
            )
            db.add(session_model)
            db.commit()
            db.refresh(session_model)
            
            return Session(
                id=session_model.id,
                session_id=session_model.session_id,
                template=session_model.template,
                created_at=session_model.created_at
            )

    @staticmethod
    def get_session(session_id: str, db: DBSession) -> Session:
        """Get session by ID"""
        session_model = db.query(SessionModel).filter(
            SessionModel.session_id == session_id
        ).first()
        
        if not session_model:
            raise SessionNotFoundException(session_id)
        
        return Session(
            id=session_model.id,
            session_id=session_model.session_id,
            template=session_model.template,
            created_at=session_model.created_at
        )

    @staticmethod
    def get_session_template(session_id: str, db: DBSession) -> str:
        """Get template for session"""
        session = SessionService.get_session(session_id, db)
        return session.template

    @staticmethod
    def delete_session(session_id: str, db: DBSession) -> bool:
        """Delete session and all related data"""
        session_model = db.query(SessionModel).filter(
            SessionModel.session_id == session_id
        ).first()
        
        if not session_model:
            return False
        
        db.delete(session_model)
        db.commit()
        return True


session_service = SessionService()