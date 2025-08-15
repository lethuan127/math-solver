"""Test configuration for math solving module."""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from ..domain.entities import MathAnswer, MathProblem, SolutionStep, User


@pytest.fixture
def sample_solution_step():
    """Sample solution step for testing."""
    return SolutionStep(
        step_number=1, description="Add the numbers together", calculation="2 + 2 = 4"
    )


@pytest.fixture
def sample_math_answer(sample_solution_step):
    """Sample math answer for testing."""
    return MathAnswer(
        question="What is 2 + 2?",
        answer_label=None,
        answer_value="4",
        explanation="Simple addition",
        steps=[sample_solution_step],
        confidence=0.95,
    )


@pytest.fixture
def sample_math_problem(sample_math_answer):
    """Sample math problem for testing."""
    return MathProblem(
        id="problem_123",
        question="What is 2 + 2?",
        answer=sample_math_answer,
        user_id="user_123",
        file_name="test.png",
        content_type="image/png",
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_user():
    """Sample user for testing."""
    return User(uid="user_123", email="test@example.com", display_name="Test User")


@pytest.fixture
def mock_ai_service():
    """Mock AI service for testing."""
    mock_service = Mock()
    mock_service.solve_problem = AsyncMock()
    return mock_service


@pytest.fixture
def mock_repository():
    """Mock repository for testing."""
    mock_repo = Mock()
    mock_repo.save_problem = AsyncMock(return_value="problem_123")
    mock_repo.get_problem = AsyncMock()
    mock_repo.get_user_problems = AsyncMock(return_value=[])
    mock_repo.delete_problem = AsyncMock(return_value=True)
    return mock_repo


@pytest.fixture
def mock_upload_file():
    """Mock upload file for testing."""
    mock_file = Mock()
    mock_file.filename = "test.png"
    mock_file.content_type = "image/png"
    mock_file.read = AsyncMock(return_value=b"fake_image_data")
    return mock_file
