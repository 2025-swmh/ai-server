from fastapi import FastAPI
from app.api import sessions

app = FastAPI(
    title="SW 연합 해커톤",
    description="SW 연합 해커톤 6팀",
    version="1.0.0"
)

# 라우터 등록
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])

# Initial API
@app.get("/")
async def root():
    return {
        "message": "SW Hackathon AI Server",
        "status": "running",
        "docs": "/docs"
    }


# Health Check API
@app.get("/health")
async def health_check():
    return {"status": "healthy"}