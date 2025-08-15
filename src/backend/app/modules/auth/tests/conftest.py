"""Test configuration for auth module."""

from unittest.mock import Mock

import pytest

from ..domain.entities import User


@pytest.fixture
def mock_firebase_client():
    """Mock Firebase client for auth tests."""
    mock_client = Mock()
    mock_client.verify_token.return_value = {
        "uid": "test_user_123",
        "email": "test@example.com",
        "name": "Test User",
        "email_verified": True,
    }
    return mock_client


@pytest.fixture
def sample_user():
    """Sample user entity for testing."""
    return User(
        uid="test_user_123",
        email="test@example.com",
        display_name="Test User",
        email_verified=True,
    )
