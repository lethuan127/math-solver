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


@patch("app.services.image_processor.ImageProcessor.process_file")
@patch("app.services.math_solver.MathSolver.solve")
def test_upload_file_success(mock_solver, mock_processor):
    # Mock the services
    mock_processor.return_value = {"text": "2 + 2 = ?", "confidence": 0.95}

    # Create a test image
    img = Image.new("RGB", (100, 100), color="white")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    response = client.post(
        "/api/v1/upload", files={"file": ("test.png", img_bytes, "image/png")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "content" in data


def test_upload_invalid_file():
    response = client.post(
        "/api/v1/upload",
        files={"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")},
    )

    assert response.status_code in [400, 422]  # May vary based on FastAPI validation
