import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.auth import AuthService, get_current_user


class TestAuthService:
    """Test cases for authentication service"""

    def setup_method(self):
        self.auth_service = AuthService()

    @patch("app.core.auth.FirebaseClient")
    @pytest.mark.asyncio
    async def test_get_current_user_success(self, mock_firebase_client_class):
        """Test successful user authentication"""
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
        mock_firebase_client.verify_token.return_value = mock_decoded_token
        
        # Create mock credentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid_token_123"
        )
        
        # Test authentication
        result = await self.auth_service.get_current_user(credentials)
        
        # Verify results
        assert result["uid"] == "test_user_123"
        assert result["email"] == "test@example.com"
        assert result["name"] == "Test User"
        assert result["email_verified"] is True
        assert "firebase_claims" in result
        
        # Verify Firebase client was called correctly
        mock_firebase_client.verify_token.assert_called_once_with("valid_token_123")

    @patch("app.core.auth.FirebaseClient")
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, mock_firebase_client_class):
        """Test authentication with invalid token"""
        # Mock Firebase client
        mock_firebase_client = MagicMock()
        mock_firebase_client_class.return_value = mock_firebase_client
        
        # Mock failed token verification
        mock_firebase_client.verify_token.return_value = None
        
        # Create mock credentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid_token"
        )
        
        # Test authentication should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await self.auth_service.get_current_user(credentials)
        
        assert exc_info.value.status_code == 401
        assert "Invalid or expired token" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_current_user_no_credentials(self):
        """Test authentication without credentials"""
        with pytest.raises(HTTPException) as exc_info:
            await self.auth_service.get_current_user(None)
        
        assert exc_info.value.status_code == 401
        assert "Authorization token required" in str(exc_info.value.detail)

    @patch("app.core.auth.FirebaseClient")
    @pytest.mark.asyncio
    async def test_get_current_user_firebase_exception(self, mock_firebase_client_class):
        """Test authentication when Firebase raises an exception"""
        # Mock Firebase client
        mock_firebase_client = MagicMock()
        mock_firebase_client_class.return_value = mock_firebase_client
        
        # Mock Firebase raising an exception
        mock_firebase_client.verify_token.side_effect = Exception("Firebase error")
        
        # Create mock credentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="some_token"
        )
        
        # Test authentication should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await self.auth_service.get_current_user(credentials)
        
        assert exc_info.value.status_code == 401
        assert "Authentication failed" in str(exc_info.value.detail)

    def test_firebase_client_lazy_initialization(self):
        """Test that Firebase client is initialized lazily"""
        auth_service = AuthService()
        assert auth_service._firebase_client is None
        
        # First call should initialize the client
        with patch("app.core.auth.FirebaseClient") as mock_firebase_client_class:
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


class TestAuthDependencies:
    """Test authentication dependency functions"""

    @patch("app.core.auth.auth_service.get_current_user")
    @pytest.mark.asyncio
    async def test_get_current_user_dependency(self, mock_auth_service):
        """Test the get_current_user dependency function"""
        # Mock auth service response
        mock_user = {
            "uid": "test_user_123",
            "email": "test@example.com"
        }
        mock_auth_service.return_value = mock_user
        
        # Create mock credentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="test_token"
        )
        
        # Test the dependency
        result = await get_current_user(credentials)
        
        assert result == mock_user
        mock_auth_service.assert_called_once_with(credentials)
