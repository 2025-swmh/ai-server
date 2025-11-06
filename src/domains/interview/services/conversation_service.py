"""
Conversation management service
Clean Architecture - Application Business Rules Layer
"""
from typing import List
from sqlalchemy.orm import Session as DBSession

from src.domains.interview.models.conversation import Conversation, Role
from src.infrastructure.database.models import ConversationModel


class ConversationService:
    """Service for managing interview conversations"""

    @staticmethod
    def save_message(
        session_id: str, 
        role: Role, 
        content: str, 
        db: DBSession
    ) -> Conversation:
        """Save a conversation message"""
        
        conversation_model = ConversationModel(
            session_id=session_id,
            role=role.value,
            content=content
        )
        
        db.add(conversation_model)
        db.commit()
        db.refresh(conversation_model)
        
        return Conversation(
            id=conversation_model.id,
            session_id=conversation_model.session_id,
            role=Role(conversation_model.role),
            content=conversation_model.content,
            created_at=conversation_model.created_at
        )

    @staticmethod
    def get_conversation_history(session_id: str, db: DBSession) -> List[Conversation]:
        """Get conversation history for a session"""
        
        conversation_models = db.query(ConversationModel).filter(
            ConversationModel.session_id == session_id
        ).order_by(ConversationModel.created_at.asc()).all()
        
        return [
            Conversation(
                id=conv.id,
                session_id=conv.session_id,
                role=Role(conv.role),
                content=conv.content,
                created_at=conv.created_at
            )
            for conv in conversation_models
        ]

    @staticmethod
    def get_conversation_history_as_dict(session_id: str, db: DBSession) -> List[dict]:
        """Get conversation history as dictionary format for AI APIs"""
        
        conversations = ConversationService.get_conversation_history(session_id, db)
        
        return [
            {
                "role": conv.role.value,
                "content": conv.content
            }
            for conv in conversations
        ]

    @staticmethod
    def delete_conversation_history(session_id: str, db: DBSession) -> int:
        """Delete all conversations for a session"""
        
        deleted_count = db.query(ConversationModel).filter(
            ConversationModel.session_id == session_id
        ).delete()
        
        db.commit()
        return deleted_count

    @staticmethod
    def get_last_message(session_id: str, db: DBSession) -> Conversation:
        """Get the last message in a conversation"""
        
        conversation_model = db.query(ConversationModel).filter(
            ConversationModel.session_id == session_id
        ).order_by(ConversationModel.created_at.desc()).first()
        
        if not conversation_model:
            return None
        
        return Conversation(
            id=conversation_model.id,
            session_id=conversation_model.session_id,
            role=Role(conversation_model.role),
            content=conversation_model.content,
            created_at=conversation_model.created_at
        )


conversation_service = ConversationService()