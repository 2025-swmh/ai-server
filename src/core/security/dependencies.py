"""
Security dependencies for the interview system
Clean Architecture - Interface Adapters Layer
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# For future authentication implementation
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    Get current user from token (placeholder for future implementation)
    """
    # For now, return None as authentication is not implemented
    # In future: decode JWT token, validate user, return user info
    return None


async def validate_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> bool:
    """
    Validate API key (placeholder for future implementation)
    """
    # For now, allow all requests
    # In future: validate API key against database
    return True


def require_auth(user: Optional[dict] = Depends(get_current_user)) -> dict:
    """
    Require authentication (placeholder for future implementation)
    """
    # For now, return empty user dict
    # In future: raise HTTPException if user is None
    if user is None:
        # Placeholder: in production, uncomment the line below
        # raise HTTPException(status_code=401, detail="Authentication required")
        logger.warning("Authentication not implemented - allowing request")
        return {"user_id": "anonymous", "role": "user"}
    
    return user


def require_admin(user: dict = Depends(require_auth)) -> dict:
    """
    Require admin role (placeholder for future implementation)
    """
    # For now, allow all authenticated requests
    # In future: check user role
    if user.get("role") != "admin":
        logger.warning("Admin check not implemented - allowing request")
        # raise HTTPException(status_code=403, detail="Admin access required")
    
    return user