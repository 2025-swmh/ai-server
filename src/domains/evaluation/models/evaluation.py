"""
Evaluation domain model
Clean Architecture - Enterprise Business Rules Layer
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import json


@dataclass
class Evaluation:
    """Evaluation domain entity"""
    session_id: str
    title: str
    interview_type: str
    evaluation_data: Dict[Any, Any]
    created_at: Optional[datetime] = None
    id: Optional[int] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def get_collaboration_profile(self) -> Optional[Dict]:
        """Get collaboration profile from evaluation data"""
        return self.evaluation_data.get('collaboration_profile')
    
    def get_interview_profile(self) -> Optional[Dict]:
        """Get interview profile from evaluation data"""
        return self.evaluation_data.get('interview_profile')
    
    def get_feedback(self) -> Optional[Dict]:
        """Get feedback from evaluation data"""
        return self.evaluation_data.get('feedback')
    
    def get_scores(self) -> Optional[Dict]:
        """Get analysis scores"""
        profile = self.get_collaboration_profile() or self.get_interview_profile()
        if profile:
            return profile.get('analysis_scores')
        return None
    
    def get_type_korean(self) -> Optional[str]:
        """Get Korean type from profile"""
        profile = self.get_collaboration_profile() or self.get_interview_profile()
        if profile:
            return profile.get('type_korean')
        return None
    
    def get_type_english(self) -> Optional[str]:
        """Get English type from profile"""
        profile = self.get_collaboration_profile() or self.get_interview_profile()
        if profile:
            return profile.get('type_english')
        return None
    
    def to_json(self) -> str:
        """Convert evaluation data to JSON string"""
        return json.dumps(self.evaluation_data, ensure_ascii=False)
    
    def __str__(self) -> str:
        return f"Evaluation(session={self.session_id}, type={self.interview_type})"