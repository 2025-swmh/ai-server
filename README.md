# SW Hackathon - Backend API

AI 기반 협업 능력 향상 플랫폼 백엔드 서버

## 🚀 빠른 시작

### 1. 가상환경 활성화
```bash
cd /Users/kdw08/Desktop/sw_hackerton
source venv/bin/activate
```

### 2. 패키지 설치
```bash
cd backend
pip install -r requirements.txt
```

### 3. 환경변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집하여 OpenAI API 키 입력
# OPENAI_API_KEY=sk-...
```

### 4. 서버 실행
```bash
# 개발 모드 (자동 리로드)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 또는 간단하게
python -m uvicorn app.main:app --reload
```

### 5. API 문서 확인
```
http://localhost:8000/docs
```

## 📁 프로젝트 구조

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱 진입점
│   ├── api/                 # API 라우터
│   │   ├── sessions.py      # 세션 관리 API
│   │   ├── chat.py          # 채팅 API
│   │   └── reports.py       # 보고서 API
│   ├── services/            # 비즈니스 로직
│   │   └── ai_service.py    # AI 응답 생성
│   ├── models/              # DB 모델 (추후 추가)
│   ├── schemas/             # Pydantic 스키마 (추후 추가)
│   └── database/            # DB 연결 (추후 추가)
├── .env                     # 환경변수
├── .gitignore
├── requirements.txt
└── README.md
```

## 🔑 주요 API 엔드포인트

### Sessions
- `POST /api/sessions/` - 새 세션 생성
- `GET /api/sessions/{session_id}` - 세션 조회
- `POST /api/sessions/{session_id}/complete` - 세션 종료

### Chat
- `POST /api/chat/` - 메시지 전송
- `WS /api/chat/ws/{session_id}` - WebSocket 실시간 채팅

### Reports
- `GET /api/reports/{report_id}` - 보고서 조회
- `GET /api/reports/user/{user_id}` - 사용자 보고서 목록
- `POST /api/reports/generate/{session_id}` - 보고서 생성

## 🛠️ 개발 팁

### 가상환경 활성화 확인
```bash
# 프롬프트 앞에 (venv)가 보이면 활성화된 것
(venv) kdw08@MacBook sw_hackerton %
```

### 가상환경 비활성화
```bash
deactivate
```

### 패키지 추가 후
```bash
pip freeze > requirements.txt
```

### 서버 재시작 없이 코드 변경
```bash
# --reload 옵션으로 실행하면 코드 변경시 자동 재시작
uvicorn app.main:app --reload
```