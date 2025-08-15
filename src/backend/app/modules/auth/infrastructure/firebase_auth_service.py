"""Firebase authentication service implementation."""

import logging
from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ...shared.database.firebase_client import FirebaseClient
from ..domain.entities import User
from ..domain.interfaces import AuthenticationService

logger = logging.getLogger(__name__)
security = HTTPBearer()


class FirebaseAuthenticationService(AuthenticationService):
    """Firebase implementation of authentication service."""

    def __init__(self):
        self._firebase_client: Optional[FirebaseClient] = None

    def get_firebase_client(self) -> FirebaseClient:
        """Get Firebase client instance (lazy initialization)."""
        if self._firebase_client is None:
            self._firebase_client = FirebaseClient()
        return self._firebase_client

    async def verify_token(self, token: str) -> User:
        """
        Verify Firebase JWT token and return user information.

        Args:
            token: The Firebase JWT token

        Returns:
            User: The authenticated user

        Raises:
            HTTPException: If token is invalid
        """
        try:
            client = self.get_firebase_client()
            decoded_token = await client.verify_token(token)

            user = User(
                uid=decoded_token.get("uid"),
                email=decoded_token.get("email"),
                display_name=decoded_token.get("name"),
                email_verified=decoded_token.get("email_verified", False),
                last_login=datetime.utcnow(),
            )

            return user

        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            ) from e

    async def get_current_user(
        self, credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> User:
        """
        Get current user from HTTP authorization credentials.

        Args:
            credentials: HTTP Authorization credentials with Bearer token

        Returns:
            User: The authenticated user

        Raises:
            HTTPException: If credentials are invalid
        """
        try:
            if not credentials:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authorization token required",
                )

            if credentials.scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme",
                )

            return await self.verify_token(credentials.credentials)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
            ) from e
