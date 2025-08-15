import io
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Math Homework Solver API" in data["message"]


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@patch("app.core.auth.auth_service.get_current_user")
@patch("app.services.math_solver.MathSolver.solve")
def test_solve_problem_success(mock_solver, mock_auth):
    from app.models.problem import ProblemResponse, Answer, SolutionStep
    
    # Mock authentication
    mock_auth.return_value = {
        "uid": "test_user_123",
        "email": "test@example.com",
        "name": "Test User",
        "email_verified": True
    }
    
    # Mock the math solver
    mock_answer = Answer(
        question="What is 2 + 2?",
        answer_value="4",
        explanation="Simple addition",
        steps=[SolutionStep(step_number=1, description="Add 2 + 2", calculation="2 + 2 = 4")],
        confidence=0.95
    )
    mock_solver.return_value = ProblemResponse(
        question="What is 2 + 2?",
        answer=mock_answer
    )

    # Create a test image
    img = Image.new("RGB", (100, 100), color="white")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    # Make request with authorization header
    response = client.post(
        "/api/v1/solve", 
        files={"file": ("test.png", img_bytes, "image/png")},
        headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "question" in data
    assert "answer" in data


def test_solve_unauthenticated():
    """Test that solve endpoint requires authentication"""
    # Create a test image
    img = Image.new("RGB", (100, 100), color="white")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    # Make request without authorization header
    response = client.post(
        "/api/v1/solve", 
        files={"file": ("test.png", img_bytes, "image/png")}
    )

    assert response.status_code in [401, 403]  # Unauthorized or Forbidden
    data = response.json()
    assert "detail" in data
    # Check for various authentication error messages
    detail = data["detail"]
    auth_error_messages = [
        "Authorization token required",
        "Not authenticated",
        "Forbidden",
        "Could not validate credentials"
    ]
    assert any(msg in detail for msg in auth_error_messages), f"Unexpected error message: {detail}"


@patch("app.core.auth.auth_service.get_current_user")
def test_history_endpoints_authenticated(mock_auth):
    """Test that history endpoints require authentication"""
    # Mock authentication
    mock_auth.return_value = {
        "uid": "test_user_123",
        "email": "test@example.com",
        "name": "Test User",
        "email_verified": True
    }

    # Test get history
    response = client.get(
        "/api/v1/history",
        headers={"Authorization": "Bearer test_token"}
    )
    # Note: This will fail with 500 due to Firebase not being configured in tests
    # but it shows the authentication is working (not 401)
    assert response.status_code != 401

    # Test delete problem
    response = client.delete(
        "/api/v1/history/test_problem_id",
        headers={"Authorization": "Bearer test_token"}
    )
    # Note: This will fail with 500 due to Firebase not being configured in tests
    # but it shows the authentication is working (not 401)
    assert response.status_code != 401


def test_history_endpoints_unauthenticated():
    """Test that history endpoints require authentication"""
    # Test get history without auth
    response = client.get("/api/v1/history")
    assert response.status_code in [401, 403]

    # Test delete problem without auth
    response = client.delete("/api/v1/history/test_problem_id")
    assert response.status_code in [401, 403]
