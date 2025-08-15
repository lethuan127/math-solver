import os
from functools import lru_cache

from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class Settings(BaseSettings):
    load_dotenv()
    """Application settings and configuration"""

    # API Settings
    api_title: str = "Math Homework Solver API"
    api_version: str = "1.0.0"
    api_description: str = "AI-powered math problem solver with OCR capabilities"

    # Environment
    environment: str = "development"
    debug: bool = True

    # Firebase Configuration
    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "")
    firebase_private_key: str = os.getenv("FIREBASE_PRIVATE_KEY", "")
    firebase_client_email: str = os.getenv("FIREBASE_CLIENT_EMAIL", "")
    firebase_storage_bucket: str = os.getenv("FIREBASE_STORAGE_BUCKET", "")

    # AI/ML Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # CORS Settings
    allowed_origins: list = ["http://localhost:3000", "http://localhost:8080"]

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra environment variables


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
