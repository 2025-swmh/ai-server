import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()


class Settings:
    
    def __init__(self):
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./interview.db")
        
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        
        self.APP_NAME = "AI Interview System"
        self.APP_VERSION = "1.0.0"
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        
        self.API_V1_PREFIX = "/api/v1"
        
        self.DEFAULT_AI_MODEL = "claude-3-haiku-20240307"
        self.DEFAULT_MAX_TOKENS = 1000
        self.DEFAULT_TEMPERATURE = 0.5
        
        self.KNOWLEDGE_BASE_MAX_LENGTH = 4000
        self.CHUNK_SIZE = 1500
        self.CHUNK_OVERLAP = 100
        
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-en-v1.5")
        self.USE_OPENAI_EMBEDDINGS = os.getenv("USE_OPENAI_EMBEDDINGS", "false").lower() == "true"


KNOWLEDGE_BASE_MAP: Dict[str, str] = {
    'backend': 'knowledge_base_backend.md',
    'frontend': 'knowledge_base_frontend.md',
    'design': 'knowledge_base_design.md',
    'planning': 'knowledge_base_planning.md',
    'cooperation': 'knowledge_base_project.md',
    'project': 'knowledge_base_project.md',
    'tenacity': 'knowledge_base_tenacity.md',
}

BASE_PROMPTS: Dict[str, Dict[str, str]] = {
    'backend': {
        'role': '시니어 백엔드 개발자 면접관',
        'situation': '주니어 백엔드 개발자 포지션 기술 면접',
        'tone': '전문적이고 정중하며, 답변이 부족하면 힌트를 제공',
        'initial_message': '안녕하세요, 면접 보러 와주셔서 감사합니다. 편하게 생각하시고 자유롭게 답변해주시면 됩니다. 먼저 간단한 질문부터 시작하겠습니다. RESTful API가 무엇인지 설명해주실 수 있나요?'
    },
    'frontend': {
        'role': '시니어 프론트엔드 개발자 면접관',
        'situation': '주니어 프론트엔드 개발자 포지션 기술 면접',
        'tone': '친절하지만 깊이 있는 질문을 던짐',
        'initial_message': '안녕하세요! 편안하게 대답해주시면 됩니다. Virtual DOM이 무엇이고 왜 사용하는지 설명해주실 수 있나요?'
    },
    'design': {
        'role': '시니어 디자이너 면접관',
        'situation': 'UI/UX 디자이너 면접',
        'tone': '사용자 중심 사고를 중시',
        'initial_message': '안녕하세요! 포트폴리오 잘 봤습니다. UI와 UX의 차이가 무엇이라고 생각하시나요?'
    },
    'planning': {
        'role': '시니어 기획자 면접관',
        'situation': '프로덕트 매니저 면접',
        'tone': '데이터 기반 의사결정을 중시',
        'initial_message': '안녕하세요! 기획 경험에 대해 이야기 나눠보겠습니다. MVP가 무엇이고 왜 중요한지 설명해주시겠어요?'
    },
    'cooperation': {
        'role': '프로젝트 매니저이자 협업 전문가',
        'situation': '팀 협업 및 커뮤니케이션 역량 평가 시뮬레이션',
        'tone': '실무적이고 구체적이며, 갈등 상황과 의사결정 과정에 집중',
        'initial_message': '사용자가 제공한 시나리오를 기반으로 협업 상황을 시뮬레이션합니다.',
        'scenario_based': True
    },
    'tenacity': {
        'role': '7년차 인사담당자 인성면접관',
        'situation': '신입/경력 채용 인성면접',
        'tone': 'STAR 기법 중심으로 구체적 경험을 질문하며, 정직성과 성장 가능성을 평가',
        'initial_message': '안녕하세요, 면접 보러 와주셔서 감사합니다. 편안한 분위기에서 진솔한 대화를 나누고 싶습니다. 먼저 간단하게 자기소개 부탁드립니다. 본인의 강점과 함께 왜 이 회사에 지원하게 되셨는지 말씀해 주시겠어요?'
    }
}

settings = Settings()