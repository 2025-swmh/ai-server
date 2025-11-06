"""
Conversation domain model
Clean Architecture - Enterprise Business Rules Layer
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class Role(str, Enum):
    """Conversation role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Conversation:
    """Conversation domain entity"""
    session_id: str
    role: Role
    content: str
    created_at: Optional[datetime] = None
    id: Optional[int] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def is_user_message(self) -> bool:
        """Check if this is a user message"""
        return self.role == Role.USER
    
    def is_assistant_message(self) -> bool:
        """Check if this is an assistant message"""
        return self.role == Role.ASSISTANT
    
    def get_preview(self, max_length: int = 50) -> str:
        """Get preview of content"""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + "..."
    
    def __str__(self) -> str:
        return f"Conversation({self.role}: {self.get_preview()})"