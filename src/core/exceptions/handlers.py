"""
Global exception handlers for the interview system
Clean Architecture - Interface Adapters Layer
"""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)


class InterviewSystemException(Exception):
    """Base exception for interview system"""
    def __init__(self, message: str, error_code: str = "INTERVIEW_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class SessionNotFoundException(InterviewSystemException):
    """Raised when session is not found"""
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session {session_id} not found",
            error_code="SESSION_NOT_FOUND"
        )


class TemplateNotFoundException(InterviewSystemException):
    """Raised when template is not found"""
    def __init__(self, template_id: str):
        super().__init__(
            message=f"Template {template_id} not found",
            error_code="TEMPLATE_NOT_FOUND"
        )


class KnowledgeBaseNotFoundException(InterviewSystemException):
    """Raised when knowledge base file is not found"""
    def __init__(self, knowledge_base: str):
        super().__init__(
            message=f"Knowledge base {knowledge_base} not found",
            error_code="KNOWLEDGE_BASE_NOT_FOUND"
        )


class AIServiceException(InterviewSystemException):
    """Raised when AI service fails"""
    def __init__(self, service: str, error: str):
        super().__init__(
            message=f"AI service {service} failed: {error}",
            error_code="AI_SERVICE_ERROR"
        )


async def interview_system_exception_handler(
    request: Request, 
    exc: InterviewSystemException
) -> JSONResponse:
    """Handle custom interview system exceptions"""
    logger.error(f"Interview system error: {exc.error_code} - {exc.message}")
    
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "detail": "Please check your request and try again"
        }
    )


async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors"""
    logger.error(f"Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "detail": exc.errors()
        }
    )


async def http_exception_handler(
    request: Request, 
    exc: StarletteHTTPException
) -> JSONResponse:
    """Handle HTTP exceptions"""
    logger.error(f"HTTP error {exc.status_code}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP_ERROR",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


async def general_exception_handler(
    request: Request, 
    exc: Exception
) -> JSONResponse:
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "detail": "Please contact support if this issue persists"
        }
    )