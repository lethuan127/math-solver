import logging

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..database.firebase_client import FirebaseClient

logger = logging.getLogger(__name__)
security = HTTPBearer()


class AuthMiddleware:
    """Firebase authentication middleware"""

    def __init__(self):
        self.firebase_client = FirebaseClient()

    async def verify_token(self, credentials: HTTPAuthorizationCredentials):
        """Verify Firebase JWT token"""
        try:
            if not credentials:
                raise HTTPException(
                    status_code=401, detail="Authorization token required"
                )

            token = credentials.credentials
            decoded_token = await self.firebase_client.verify_token(token)

            if not decoded_token:
                raise HTTPException(status_code=401, detail="Invalid or expired token")

            return decoded_token

        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise HTTPException(status_code=401, detail="Authentication failed") from e


# Global middleware instance
auth_middleware = AuthMiddleware()
