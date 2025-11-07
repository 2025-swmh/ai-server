"""
FastAPI application entry point
Clean Architecture - Interface Adapters Layer
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
import logging

from src.core.config.settings import settings
from src.core.exceptions.handlers import (
    InterviewSystemException,
    interview_system_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)

from src.api.v1.router import api_router

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(InterviewSystemException, interview_system_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Interview System API",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting up")
    logger.info(f"📍 API documentation: http://localhost:8000/docs")
    logger.info(f"🔑 Anthropic API: {'✅ Configured' if settings.ANTHROPIC_API_KEY else '❌ Missing'}")
    logger.info(f"🏗️ Environment: {'🐛 Development' if settings.DEBUG else '🚀 Production'}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info(f"🛑 {settings.APP_NAME} shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="192.168.12.146",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )