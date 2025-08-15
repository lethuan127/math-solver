"""Domain interfaces for authentication module."""

from abc import ABC, abstractmethod

from .entities import User


class AuthenticationService(ABC):
    """Interface for authentication service."""

    @abstractmethod
    async def verify_token(self, token: str) -> User:
        """
        Verify an authentication token and return user info.

        Args:
            token: The JWT token to verify

        Returns:
            User: The authenticated user

        Raises:
            AuthenticationError: If token is invalid
        """
        pass

    @abstractmethod
    async def get_current_user(self, credentials) -> User:
        """
        Get current user from request credentials.

        Args:
            credentials: HTTP authorization credentials

        Returns:
            User: The authenticated user

        Raises:
            AuthenticationError: If credentials are invalid
        """
        pass
