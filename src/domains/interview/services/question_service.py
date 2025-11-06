"""
Interview question generation service
Clean Architecture - Application Business Rules Layer
"""
from typing import Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from src.core.config.settings import BASE_PROMPTS, KNOWLEDGE_BASE_MAP
from src.infrastructure.database.models import SessionModel
from src.infrastructure.external_services.claude_client import claude_client
from src.infrastructure.external_services.knowledge_loader import knowledge_loader
from src.domains.session.services.session_service import session_service
from src.domains.interview.services.conversation_service import conversation_service
from src.domains.interview.models.conversation import Role


class QuestionService:
    """Service for generating interview questions"""

    @staticmethod
    def _get_template_config(session_id: str, db: Session) -> Dict:
        """Get template configuration for session"""
        try:
            session_domain = session_service.get_session(session_id, db)
            template_id = session_domain.template
        except:
            template_id = 'backend'
        
        if template_id not in BASE_PROMPTS:
            template_id = 'backend'
            
        return BASE_PROMPTS[template_id], template_id

    @staticmethod
    async def generate_first_question(
        session_id: str, 
        db: Session, 
        scenario: Optional[str] = None
    ) -> Dict:
        """Generate the first question for an interview session"""
        
        # Get template configuration
        template_config, template_id = QuestionService._get_template_config(session_id, db)
        
        # Load knowledge base
        knowledge_base_file = KNOWLEDGE_BASE_MAP.get(template_id, 'knowledge_base_project.md')
        knowledge_base = knowledge_loader.load_knowledge_base(knowledge_base_file)
        
        # Create system prompt
        if template_id == 'cooperation' and scenario:
            # Special handling for cooperation template with scenario
            system_prompt = f"""당신은 협업 상황 시뮬레이션의 진행자입니다.

**시뮬레이션 목표**: 실제 협업 상황을 재현하여 사용자가 직접 그 상황에 참여하도록 합니다.

**지식 베이스**:
{knowledge_base}

**주어진 시나리오**:
{scenario}

**시뮬레이션 지침**:
1. 사용자를 실제 협업 상황 속 핵심 인물로 배치하세요
2. 다른 팀원들(백엔드/프론트엔드/기획자 등)의 역할을 연기하여 갈등 상황을 재현하세요
3. 사용자에게 "어떻게 하시겠습니까?" 같은 질문보다는 실제 상황을 제시하고 반응을 기다리세요
4. 마치 실제 회의실에 있는 것처럼 생생한 상황을 만드세요

**예시 진행 방식**:
- "팀장님, 급한 상황이 생겼습니다. 백엔드 김개발님과 프론트엔드 박코딩님이 API 스펙 문제로 지금 회의실에서 대화 중입니다."
- "김개발: '이 API 구조는 성능상 문제가 있어요. 데이터 구조를 바꿔야 합니다.'"
- "박코딩: '그럼 우리가 이미 개발한 화면을 다 수정해야 하는데요? 일정이 촉박합니다.'"

시나리오를 바탕으로 생생한 협업 갈등 상황을 재현하여 사용자가 그 상황에 직접 개입할 수 있도록 시뮬레이션을 시작하세요."""
            
            user_message = f"주어진 시나리오 '{scenario}'를 바탕으로 협업 시뮬레이션을 시작하겠습니다. 인사와 함께 첫 번째 상황을 제시하고 질문해주세요."
        else:
            # Standard template handling
            system_prompt = f"""당신은 {template_config['role']}입니다.

**상황**: {template_config['situation']}  
**톤**: {template_config['tone']}

**지식 베이스**:
{knowledge_base}

면접을 자연스럽게 시작하고 첫 번째 질문을 해주세요."""
            
            user_message = "면접을 시작하겠습니다. 인사와 함께 첫 질문을 해주세요."
        
        # Generate AI response
        ai_response = await claude_client.generate_message(
            system_prompt=system_prompt,
            user_message=user_message,
            max_tokens=500,
            temperature=0.7
        )
        
        # Save to database using conversation service
        conversation_service.save_message(session_id, Role.ASSISTANT, ai_response, db)
        
        return {
            "message": ai_response,
            "session_id": session_id,
            "template_id": template_id,
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    async def generate_response(
        session_id: str,
        user_message: str,
        db: Session
    ) -> Dict:
        """Generate AI response to user message"""
        
        # Save user message
        conversation_service.save_message(session_id, Role.USER, user_message, db)
        
        # Get template configuration
        template_config, template_id = QuestionService._get_template_config(session_id, db)
        
        # Load knowledge base
        knowledge_base_file = KNOWLEDGE_BASE_MAP.get(template_id, 'knowledge_base_project.md')
        knowledge_base = knowledge_loader.load_knowledge_base(knowledge_base_file)
        
        # Get conversation history
        history = conversation_service.get_conversation_history_as_dict(session_id, db)
        
        # Create system prompt
        if template_id == 'cooperation':
            system_prompt = f"""당신은 협업 상황 시뮬레이션의 진행자입니다.

**시뮬레이션 목표**: 실제 협업 상황을 재현하여 사용자가 직접 그 상황에 참여하도록 합니다.

**지식 베이스**:
{knowledge_base}

**시뮬레이션 지침**:
1. 사용자의 행동/발언에 따라 다른 팀원들의 반응을 연기하여 보여주세요
2. 실제 협업에서 일어날 수 있는 현실적인 반응과 갈등을 재현하세요
3. 팀원들의 대화를 직접 인용부호로 표현하여 생생함을 더하세요
4. 사용자의 대응에 따라 상황이 좋아지거나 악화되는 것을 보여주세요

**진행 방식**:
- 팀원들의 실제 발언을 재현: "김개발: '하지만 이렇게 하면...'"
- 상황의 변화를 설명: "박코딩님이 표정이 굳어지며..."
- 새로운 문제 상황 추가: "그때 기획팀에서 급히 연락이 왔습니다."

사용자의 이전 행동에 대한 팀원들의 반응을 보여주고, 다음 협업 상황을 실감나게 전개하세요."""
        else:
            system_prompt = f"""당신은 {template_config['role']}입니다.

**상황**: {template_config['situation']}
**톤**: {template_config['tone']}

**지식 베이스**:
{knowledge_base}

지금까지의 대화를 바탕으로 적절한 후속 질문을 해주세요."""
        
        # Generate AI response with conversation history
        ai_response = await claude_client.generate_message_with_history(
            system_prompt=system_prompt,
            messages=history,
            max_tokens=500,
            temperature=0.7
        )
        
        # Save AI response
        conversation_service.save_message(session_id, Role.ASSISTANT, ai_response, db)
        
        return {
            "message": ai_response,
            "session_id": session_id,
            "template_id": template_id,
            "timestamp": datetime.now().isoformat()
        }


question_service = QuestionService()