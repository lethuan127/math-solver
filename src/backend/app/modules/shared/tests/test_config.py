"""Tests for configuration management."""

import os
from unittest.mock import patch

from ..config import Settings, get_settings


class TestSettings:
    """Test cases for Settings class."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()

        assert settings.api_title == "Math Homework Solver API"
        assert settings.api_version == "1.0.0"
        # Note: environment will be "test" in test environment due to conftest.py
        assert settings.environment in ["development", "test"]
        assert settings.debug is True
        assert isinstance(settings.allowed_origins, list)

    @patch.dict(
        os.environ,
        {
            "API_TITLE": "Custom API Title",
            "API_VERSION": "2.0.0",
            "ENVIRONMENT": "production",
            "DEBUG": "false",
            "FIREBASE_PROJECT_ID": "custom-project",
            "OPENAI_API_KEY": "custom-key",
        },
    )
    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        settings = Settings()

        assert settings.api_title == "Custom API Title"
        assert settings.api_version == "2.0.0"
        assert settings.environment == "production"
        assert settings.debug is False
        assert settings.firebase_project_id == "custom-project"
        assert settings.openai_api_key == "custom-key"

    def test_firebase_configuration(self):
        """Test Firebase configuration fields."""
        settings = Settings()

        # These should exist even if empty
        assert hasattr(settings, "firebase_project_id")
        assert hasattr(settings, "firebase_private_key")
        assert hasattr(settings, "firebase_client_email")
        assert hasattr(settings, "firebase_storage_bucket")

    def test_cors_origins(self):
        """Test CORS origins configuration."""
        settings = Settings()

        assert "http://localhost:3000" in settings.allowed_origins
        assert "http://localhost:8080" in settings.allowed_origins


class TestGetSettings:
    """Test cases for get_settings function."""

    def test_get_settings_caching(self):
        """Test that get_settings returns cached instance."""
        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    def test_get_settings_returns_settings_instance(self):
        """Test that get_settings returns Settings instance."""
        settings = get_settings()

        assert isinstance(settings, Settings)
