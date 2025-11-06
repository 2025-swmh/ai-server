"""
Session domain model
Clean Architecture - Enterprise Business Rules Layer
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Session:
    """Session domain entity"""
    session_id: str
    template: str
    created_at: Optional[datetime] = None
    id: Optional[int] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def is_valid_template(self) -> bool:
        """Check if template is valid"""
        valid_templates = ['cooperation', 'backend', 'frontend', 'design', 'planning', 'tenacity']
        return self.template in valid_templates
    
    def __str__(self) -> str:
        return f"Session(id={self.session_id}, template={self.template})"