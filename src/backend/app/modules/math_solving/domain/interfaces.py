"""Domain interfaces for math solving module."""

from abc import ABC, abstractmethod
from typing import Optional

from fastapi import UploadFile

from .entities import MathAnswer, MathProblem, User


class MathSolverRepository(ABC):
    """Repository interface for math solver data persistence."""

    @abstractmethod
    async def save_problem(self, problem: MathProblem) -> str:
        """Save a math problem and return its ID."""
        pass

    @abstractmethod
    async def get_problem(self, problem_id: str, user_id: str) -> Optional[MathProblem]:
        """Get a specific problem by ID for a user."""
        pass

    @abstractmethod
    async def get_user_problems(
        self, user_id: str, limit: int = 50
    ) -> list[MathProblem]:
        """Get all problems for a user."""
        pass

    @abstractmethod
    async def delete_problem(self, problem_id: str, user_id: str) -> bool:
        """Delete a problem. Returns True if deleted, False if not found."""
        pass


class AIService(ABC):
    """Interface for AI-powered math solving service."""

    @abstractmethod
    async def solve_problem(self, image_file: UploadFile) -> MathAnswer:
        """Solve a math problem from an image file."""
        pass


class AuthenticationService(ABC):
    """Interface for authentication service."""

    @abstractmethod
    async def verify_token(self, token: str) -> User:
        """Verify an authentication token and return user info."""
        pass

    @abstractmethod
    async def get_current_user(self, credentials) -> User:
        """Get current user from request credentials."""
        pass
