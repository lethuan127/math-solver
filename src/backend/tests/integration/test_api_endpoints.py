"""Integration tests for API endpoints."""

import io
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.modules.math_solving.domain.entities import (
    MathAnswer,
    MathProblem,
    SolutionStep,
    User,
)

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Math Homework Solver API" in data["message"]


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@patch("app.modules.shared.container.container.solve_math_problem_use_case")
@patch("app.modules.shared.container.container.auth_service")
def test_solve_problem_success(mock_auth_container, mock_use_case_container):
    """Test successful problem solving."""
    # Mock authentication service
    mock_auth_service = Mock()
    mock_user = User(
        uid="test_user_123",
        email="test@example.com",
        display_name="Test User",
        email_verified=True,
    )
    mock_auth_service.get_current_user = AsyncMock(return_value=mock_user)
    mock_auth_container.return_value = mock_auth_service

    # Mock use case
    mock_use_case = Mock()
    mock_answer = MathAnswer(
        question="What is 2 + 2?",
        answer_label=None,
        answer_value="4",
        explanation="Simple addition",
        steps=[
            SolutionStep(
                step_number=1, description="Add 2 + 2", calculation="2 + 2 = 4"
            )
        ],
        confidence=0.95,
    )
    mock_problem = MathProblem(
        id="problem_123",
        question="What is 2 + 2?",
        answer=mock_answer,
        user_id="test_user_123",
        file_name="test.png",
        content_type="image/png",
        created_at=datetime.utcnow(),
    )
    mock_use_case.execute = AsyncMock(return_value=mock_problem)
    mock_use_case_container.return_value = mock_use_case

    # Create a test image
    img = Image.new("RGB", (100, 100), color="white")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    # Make request with authorization header
    response = client.post(
        "/api/v1/solve",
        files={"file": ("test.png", img_bytes, "image/png")},
        headers={"Authorization": "Bearer test_token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "question" in data
    assert "answer" in data
    assert data["question"] == "What is 2 + 2?"
    assert data["answer"]["answer_value"] == "4"


def test_solve_unauthenticated():
    """Test that solve endpoint requires authentication."""
    # Create a test image
    img = Image.new("RGB", (100, 100), color="white")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    # Make request without authorization header
    response = client.post(
        "/api/v1/solve", files={"file": ("test.png", img_bytes, "image/png")}
    )

    assert response.status_code in [
        401,
        403,
        422,
    ]  # Unauthorized, Forbidden, or Validation Error


@patch("app.modules.shared.container.container.get_user_history_use_case")
@patch("app.modules.shared.container.container.auth_service")
def test_history_endpoints_authenticated(
    mock_auth_container, mock_history_use_case_container
):
    """Test that history endpoints work with authentication."""
    # Mock authentication service
    mock_auth_service = Mock()
    mock_user = User(
        uid="test_user_123",
        email="test@example.com",
        display_name="Test User",
        email_verified=True,
    )
    mock_auth_service.get_current_user = AsyncMock(return_value=mock_user)
    mock_auth_container.return_value = mock_auth_service

    # Mock history use case
    mock_use_case = Mock()
    mock_use_case.execute = AsyncMock(return_value=[])
    mock_history_use_case_container.return_value = mock_use_case

    # Test get history
    response = client.get(
        "/api/v1/history", headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "history" in data
    assert "user_id" in data
    assert "total_problems" in data


@patch("app.modules.shared.container.container.delete_problem_use_case")
@patch("app.modules.shared.container.container.auth_service")
def test_delete_problem_authenticated(
    mock_auth_container, mock_delete_use_case_container
):
    """Test that delete endpoint works with authentication."""
    # Mock authentication service
    mock_auth_service = Mock()
    mock_user = User(
        uid="test_user_123",
        email="test@example.com",
        display_name="Test User",
        email_verified=True,
    )
    mock_auth_service.get_current_user = AsyncMock(return_value=mock_user)
    mock_auth_container.return_value = mock_auth_service

    # Mock delete use case
    mock_use_case = Mock()
    mock_use_case.execute = AsyncMock(return_value=True)
    mock_delete_use_case_container.return_value = mock_use_case

    # Test delete problem
    response = client.delete(
        "/api/v1/history/test_problem_id",
        headers={"Authorization": "Bearer test_token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "problem_id" in data
    assert "user_id" in data


def test_history_endpoints_unauthenticated():
    """Test that history endpoints require authentication."""
    # Test get history without auth
    response = client.get("/api/v1/history")
    assert response.status_code in [401, 403, 422]

    # Test delete problem without auth
    response = client.delete("/api/v1/history/test_problem_id")
    assert response.status_code in [401, 403, 422]
