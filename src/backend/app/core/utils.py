import hashlib
import json
import logging
from datetime import datetime
from typing import Any


def setup_logging(level: str = "INFO") -> None:
    """Setup application logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
    )


def generate_file_hash(content: bytes) -> str:
    """Generate SHA-256 hash for file content"""
    return hashlib.sha256(content).hexdigest()


def format_timestamp(dt: datetime | None = None) -> str:
    """Format datetime to ISO string"""
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat()


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove potentially dangerous characters
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
    return "".join(c for c in filename if c in safe_chars)


def validate_json(data: str) -> dict[Any, Any] | None:
    """Validate and parse JSON string"""
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None
