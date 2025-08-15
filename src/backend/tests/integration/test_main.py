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


@patch("app.services.math_solver.MathSolver.solve")
def test_solve_problem_success(mock_solver):
    from app.models.problem import ProblemResponse, Answer, SolutionStep
    
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

    response = client.post(
        "/api/v1/solve", files={"file": ("test.png", img_bytes, "image/png")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "question" in data
    assert "answer" in data


def test_solve_invalid_file():
    response = client.post(
        "/api/v1/solve",
        files={"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")},
    )

    assert response.status_code == 500  # Internal server error due to invalid file type
