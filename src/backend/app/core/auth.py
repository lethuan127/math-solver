import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..database.firebase_client import FirebaseClient

logger = logging.getLogger(__name__)
security = HTTPBearer()


class AuthService:
    """Authentication service for API endpoints"""

    def __init__(self):
        self._firebase_client: Optional[FirebaseClient] = None

    def get_firebase_client(self) -> FirebaseClient:
        """Get Firebase client instance (lazy initialization)"""
        if self._firebase_client is None:
            self._firebase_client = FirebaseClient()
        return self._firebase_client

    async def get_current_user(
        self, credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> dict:
        """
        Verify Firebase JWT token and return user information
        
        Args:
            credentials: HTTP Authorization credentials with Bearer token
            
        Returns:
            dict: Decoded user information from Firebase token
            
        Raises:
            HTTPException: If token is invalid or verification fails
        """
        try:
            if not credentials:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authorization token required",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            token = credentials.credentials
            firebase_client = self.get_firebase_client()
            decoded_token = await firebase_client.verify_token(token)

            if not decoded_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Extract user information
            user_info = {
                "uid": decoded_token.get("uid"),
                "email": decoded_token.get("email"),
                "name": decoded_token.get("name"),
                "email_verified": decoded_token.get("email_verified", False),
                "firebase_claims": decoded_token,
            }

            logger.info(f"User authenticated: {user_info['uid']}")
            return user_info

        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e


# Global auth service instance
auth_service = AuthService()


# Dependency function for use in endpoints
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Dependency function to get current authenticated user
    
    Usage in endpoints:
    @router.get("/protected")
    async def protected_endpoint(current_user: dict = Depends(get_current_user)):
        user_id = current_user["uid"]
        ...
    """
    return await auth_service.get_current_user(credentials)


# Optional dependency - allows endpoints to work with or without auth
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[dict]:
    """
    Optional authentication dependency - returns None if no token provided
    
    Usage in endpoints that can work with or without authentication:
    @router.get("/optional-auth")
    async def optional_endpoint(current_user: Optional[dict] = Depends(get_current_user_optional)):
        if current_user:
            user_id = current_user["uid"]
        else:
            # Handle anonymous access
            ...
    """
    if not credentials:
        return None
    
    try:
        return await auth_service.get_current_user(credentials)
    except HTTPException:
        return None
