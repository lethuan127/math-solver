"""Tests for Firebase authentication service."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from ..domain.entities import User
from ..infrastructure.firebase_auth_service import FirebaseAuthenticationService


class TestFirebaseAuthenticationService:
    """Test cases for Firebase authentication service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.auth_service = FirebaseAuthenticationService()

    @patch("app.modules.auth.infrastructure.firebase_auth_service.FirebaseClient")
    @pytest.mark.asyncio
    async def test_verify_token_success(self, mock_firebase_client_class):
        """Test successful token verification."""
        # Mock Firebase client
        mock_firebase_client = MagicMock()
        mock_firebase_client_class.return_value = mock_firebase_client

        # Mock successful token verification
        mock_decoded_token = {
            "uid": "test_user_123",
            "email": "test@example.com",
            "name": "Test User",
            "email_verified": True,
        }
        mock_firebase_client.verify_token = AsyncMock(return_value=mock_decoded_token)

        # Test token verification
        result = await self.auth_service.verify_token("valid_token_123")

        # Verify results
        assert isinstance(result, User)
        assert result.uid == "test_user_123"
        assert result.email == "test@example.com"
        assert result.display_name == "Test User"
        assert result.email_verified is True
        assert isinstance(result.last_login, datetime)

        # Verify Firebase client was called correctly
        mock_firebase_client.verify_token.assert_called_once_with("valid_token_123")

    @patch("app.modules.auth.infrastructure.firebase_auth_service.FirebaseClient")
    @pytest.mark.asyncio
    async def test_verify_token_invalid_token(self, mock_firebase_client_class):
        """Test token verification with invalid token."""
        # Mock Firebase client
        mock_firebase_client = MagicMock()
        mock_firebase_client_class.return_value = mock_firebase_client

        # Mock failed token verification
        mock_firebase_client.verify_token = AsyncMock(
            side_effect=Exception("Invalid token")
        )

        # Test token verification should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await self.auth_service.verify_token("invalid_token")

        assert exc_info.value.status_code == 401
        assert "Invalid or expired token" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_current_user_success(self):
        """Test successful user authentication via get_current_user."""
        with patch.object(self.auth_service, "verify_token") as mock_verify:
            # Mock successful verification
            expected_user = User(
                uid="test_user_123", email="test@example.com", display_name="Test User"
            )
            mock_verify.return_value = expected_user

            # Create mock credentials
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer", credentials="valid_token_123"
            )

            # Test authentication
            result = await self.auth_service.get_current_user(credentials)

            assert result == expected_user
            mock_verify.assert_called_once_with("valid_token_123")

    @pytest.mark.asyncio
    async def test_get_current_user_no_credentials(self):
        """Test authentication without credentials."""
        with pytest.raises(HTTPException) as exc_info:
            await self.auth_service.get_current_user(None)

        assert exc_info.value.status_code == 401
        assert "Authorization token required" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_scheme(self):
        """Test authentication with invalid scheme."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Basic", credentials="some_token"
        )

        with pytest.raises(HTTPException) as exc_info:
            await self.auth_service.get_current_user(credentials)

        assert exc_info.value.status_code == 401
        assert "Invalid authentication scheme" in str(exc_info.value.detail)

    def test_firebase_client_lazy_initialization(self):
        """Test that Firebase client is initialized lazily."""
        auth_service = FirebaseAuthenticationService()
        assert auth_service._firebase_client is None

        # First call should initialize the client
        with patch(
            "app.modules.auth.infrastructure.firebase_auth_service.FirebaseClient"
        ) as mock_firebase_client_class:
            mock_client = MagicMock()
            mock_firebase_client_class.return_value = mock_client

            client1 = auth_service.get_firebase_client()
            assert client1 == mock_client
            assert auth_service._firebase_client == mock_client

            # Second call should return the same instance
            client2 = auth_service.get_firebase_client()
            assert client2 == mock_client

            # Firebase client should only be instantiated once
            mock_firebase_client_class.assert_called_once()
