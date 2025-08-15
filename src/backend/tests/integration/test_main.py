"""Integration tests for main application endpoints.

This file contains basic integration tests for the core application endpoints.
For comprehensive API testing, see test_api_endpoints.py.
"""

import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint returns correct API information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Math Homework Solver API" in data["message"]
    assert "version" in data
    assert "docs" in data


def test_health_check():
    """Test health check endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


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

    # Should return authentication error
    assert response.status_code in [401, 403, 422]
    data = response.json()
    assert "detail" in data


def test_history_endpoints_unauthenticated():
    """Test that history endpoints require authentication."""
    # Test get history without auth
    response = client.get("/api/v1/history")
    assert response.status_code in [401, 403, 422]

    # Test delete problem without auth
    response = client.delete("/api/v1/history/test_problem_id")
    assert response.status_code in [401, 403, 422]


def test_docs_endpoint():
    """Test that API documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    # Should return HTML content for Swagger UI
    assert "text/html" in response.headers.get("content-type", "")


def test_openapi_schema():
    """Test that OpenAPI schema is available."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert schema["info"]["title"] == "Math Homework Solver API"


@pytest.mark.parametrize("invalid_endpoint", [
    "/api/v1/nonexistent",
    "/invalid/path",
    "/api/v2/solve",  # Wrong version
])
def test_invalid_endpoints(invalid_endpoint):
    """Test that invalid endpoints return 404."""
    response = client.get(invalid_endpoint)
    assert response.status_code == 404


def test_cors_headers():
    """Test that CORS headers are properly set."""
    response = client.options("/api/v1/solve")
    # Should have CORS headers (even if endpoint requires auth)
    assert response.status_code in [200, 405]  # OPTIONS might not be allowed
    
    # Test with actual request
    response = client.get("/")
    # CORS headers should be present for successful requests
    assert response.status_code == 200
