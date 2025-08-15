"""Tests for auth domain entities."""

from datetime import datetime

from ..domain.entities import User


class TestUser:
    """Test cases for User entity."""

    def test_user_creation(self):
        """Test creating a user entity."""
        user = User(
            uid="test_user_123",
            email="test@example.com",
            display_name="Test User",
            email_verified=True,
        )

        assert user.uid == "test_user_123"
        assert user.email == "test@example.com"
        assert user.display_name == "Test User"
        assert user.email_verified is True
        assert user.created_at is None
        assert user.last_login is None

    def test_user_with_timestamps(self):
        """Test creating a user with timestamps."""
        created_at = datetime.utcnow()
        last_login = datetime.utcnow()

        user = User(
            uid="test_user_123",
            email="test@example.com",
            created_at=created_at,
            last_login=last_login,
        )

        assert user.created_at == created_at
        assert user.last_login == last_login

    def test_user_minimal_data(self):
        """Test creating a user with minimal required data."""
        user = User(uid="test_user_123")

        assert user.uid == "test_user_123"
        assert user.email is None
        assert user.display_name is None
        assert user.email_verified is False
