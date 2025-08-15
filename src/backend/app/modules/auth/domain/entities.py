"""Domain entities for authentication module."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """A user of the system."""

    uid: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    email_verified: bool = False
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
