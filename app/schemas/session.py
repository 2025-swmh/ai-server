from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    session_id: str = Field(..., description="세션 ID")
    template: str = Field(..., description="템플릿 타입")
