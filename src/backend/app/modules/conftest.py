"""Shared test configuration for all modules."""

import asyncio
import os
from unittest.mock import patch

import pytest

# Set test environment variables
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "true"
os.environ["FIREBASE_PROJECT_ID"] = "test-project"
os.environ["FIREBASE_PRIVATE_KEY"] = "test-key"
os.environ["FIREBASE_CLIENT_EMAIL"] = "test@test.com"
os.environ["OPENAI_API_KEY"] = "test-key"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def mock_firebase_init():
    """Mock Firebase initialization for all tests."""
    with patch("firebase_admin.initialize_app"), patch(
        "firebase_admin.credentials.Certificate"
    ), patch("firebase_admin.firestore.client"), patch("firebase_admin.storage.bucket"):
        yield


@pytest.fixture
def sample_user():
    """Sample user for testing."""
    from app.modules.auth.domain.entities import User

    return User(
        uid="test_user_123",
        email="test@example.com",
        display_name="Test User",
        email_verified=True,
    )


@pytest.fixture
def sample_math_problem():
    """Sample math problem for testing."""
    return {"text": "2 + 2 = ?", "problem_type": "arithmetic", "difficulty": "easy"}


@pytest.fixture
def sample_solution():
    """Sample solution for testing."""
    return {
        "solution": "4",
        "steps": ["2 + 2", "= 4"],
        "explanation": "Simple addition of two numbers",
    }
