"""
Evaluation service for interview assessments
Clean Architecture - Application Business Rules Layer
"""
import json
from typing import Dict, List
from sqlalchemy.orm import Session
from json_repair import repair_json

from src.core.config.settings import KNOWLEDGE_BASE_MAP
from src.infrastructure.database.models import EvaluationModel
from src.infrastructure.external_services.claude_client import claude_client
from src.infrastructure.external_services.knowledge_loader import knowledge_loader
from src.domains.session.services.session_service import session_service
from src.domains.interview.services.conversation_service import conversation_service
from src.domains.evaluation.models.evaluation import Evaluation


class EvaluationService:
    """Service for generating interview evaluations"""

    @staticmethod
    def _get_conversation_history(session_id: str, db: Session) -> List[Dict]:
        """Get conversation history for evaluation"""
        return conversation_service.get_conversation_history_as_dict(session_id, db)

    @staticmethod
    def _save_evaluation(evaluation_data: Dict, db: Session) -> EvaluationModel:
        """Save evaluation result to database"""
        # Check if evaluation already exists
        existing = db.query(EvaluationModel).filter(
            EvaluationModel.session_id == evaluation_data["session_id"]
        ).first()
        
        if existing:
            # Update existing evaluation
            existing.title = evaluation_data.get("title")
            existing.evaluation_json = json.dumps(evaluation_data, ensure_ascii=False)
            evaluation_obj = existing
        else:
            # Create new evaluation
            evaluation_obj = EvaluationModel(
                session_id=evaluation_data["session_id"],
                title=evaluation_data.get("title"),
                interview_type=evaluation_data.get("template_type", "cooperation"),
                evaluation_json=json.dumps(evaluation_data, ensure_ascii=False)
            )
            db.add(evaluation_obj)
        
        db.commit()
        db.refresh(evaluation_obj)
        return evaluation_obj

    @staticmethod
    async def generate_cooperation_evaluation(session_id: str, db: Session) -> Dict:
        """Generate cooperation evaluation based on conversation history"""
        
        # Get session info
        session_domain = session_service.get_session(session_id, db)
        
        if session_domain.template != 'cooperation':
            raise ValueError(f"협업 평가는 cooperation 템플릿에서만 사용 가능합니다. (현재: {session_domain.template})")
        
        # Get conversation history
        history = EvaluationService._get_conversation_history(session_id, db)
        
        if not history:
            raise ValueError(f"세션 {session_id}에 대화 내역이 없습니다.")
        
        # Load knowledge base
        knowledge_base = knowledge_loader.load_knowledge_base('knowledge_base_project.md')
        
        # Create evaluation prompt
        system_prompt = f"""당신은 협업 및 소통 능력을 평가하는 전문 평가자입니다.

**평가 기준 지식 베이스:**
{knowledge_base}

**평가 기준:**
1. relationship_contribution (관계 기여도): 상/중/하
   - 상: 감정적 언어를 최소화하고 팀원 의견을 경청/통합하며, 팀 사기와 안정화에 크게 기여
   - 중: 기본적인 협력 태도는 있으나 적극적인 관계 형성이나 갈등 중재는 부족
   - 하: 방어적 태도나 일방적 주장으로 팀 분위기에 부정적 영향

2. problem_leadership (문제 주도성): 상/중/하
   - 상: 문제 발생 시 즉각 해결 방안을 제시하고 역할/책임을 명확히 분배하며 실행을 주도
   - 중: 문제 인식은 하나 구체적 해결책 제시나 실행 주도는 부족
   - 하: 문제를 회피하거나 의존적인 태도

**협업 유형:**
- 관계 안정화 촉진자 [relationship_contribution: 상 / problem_leadership: 중]
- 실행 주도 전략가 [relationship_contribution: 중 / problem_leadership: 상]
- 비전 통합 분석가 [relationship_contribution: 상 / problem_leadership: 상]
- 유연한 실행 지원가 [relationship_contribution: 중 / problem_leadership: 하]

**응답 형식:**
반드시 아래 JSON 형식으로만 응답하세요.

{{
  "session_id": "{session_id}",
  "title": "대화내용을 바탕으로 한 제목",
  "template_type": "cooperation",
  "collaboration_profile": {{
    "type_korean": "관계 안정화 촉진자",
    "type_english": "Relationship Stabilizer",
    "description_summary": "협업 시뮬레이션에서 나타난 참가자의 특성을 요약",
    "analysis_scores": {{
      "relationship_contribution": "상",
      "problem_leadership": "중"
    }}
  }},
  "feedback": {{
    "good_points": [
      {{
        "area": "커뮤니케이션",
        "detail": "구체적인 칭찬 내용"
      }}
    ],
    "improvement_points": [
      {{
        "area": "문제 해결 주도성",
        "detail": "개선이 필요한 부분 설명",
        "action_plan": "구체적인 개선 방법"
      }}
    ]
  }},
  "appeal_recommendation": {{
    "core_keywords": ["효과적인 협업", "갈등 조정 능력"],
    "example_statements": [
      {{
        "category": "자소서 (협업 역량)",
        "statement": "AI 분석 결과를 활용한 자소서 예시"
      }}
    ]
  }}
}}

**중요:**
- 대화 내용을 꼼꼼히 분석하여 참가자의 협업 방식과 커뮤니케이션 패턴을 파악하세요
- 시나리오 기반 협업 시뮬레이션에서 나타난 구체적인 행동을 평가하세요
- JSON 형식을 정확히 지켜주세요"""

        # Convert conversation to text
        conversation_text = "\n\n".join([
            f"{'AI 면접관' if msg['role'] == 'assistant' else '참가자'}: {msg['content']}"
            for msg in history
        ])

        user_prompt = f"""아래는 협업 시뮬레이션 대화 내역입니다. 이를 분석하여 평가 결과를 JSON 형식으로 생성하세요.

**대화 내역:**
{conversation_text}

위 대화를 분석하여 참가자의 협업 역량, 커뮤니케이션 능력, 갈등 해결 능력을 평가하고 JSON으로 출력하세요."""

        # Generate evaluation with Claude
        ai_response = await claude_client.generate_message(
            system_prompt=system_prompt,
            user_message=user_prompt,
            max_tokens=4000,
            temperature=0.3
        )

        # Parse JSON response
        try:
            json_text = ai_response.strip()
            if json_text.startswith("```json"):
                json_text = json_text.split("```json")[1].split("```")[0].strip()
            elif json_text.startswith("```"):
                json_text = json_text.split("```")[1].split("```")[0].strip()

            repaired_json = repair_json(json_text)
            evaluation_result = json.loads(repaired_json)
            
            # Save evaluation to database
            EvaluationService._save_evaluation(evaluation_result, db)
            
            return evaluation_result

        except Exception as e:
            raise ValueError(f"AI 응답을 JSON으로 파싱할 수 없습니다: {str(e)}")

    @staticmethod
    async def generate_evaluation(session_id: str, db: Session) -> Dict:
        """Generate evaluation based on template type"""
        
        # Get session to determine template
        session_domain = session_service.get_session(session_id, db)
        template = session_domain.template
        
        if template == 'cooperation':
            return await EvaluationService.generate_cooperation_evaluation(session_id, db)
        else:
            raise ValueError(f"지원하지 않는 템플릿입니다: {template}")


evaluation_service = EvaluationService()