"""Dependency injection container for the application."""

from functools import lru_cache

from ..auth.domain.interfaces import AuthenticationService
from ..auth.infrastructure.firebase_auth_service import FirebaseAuthenticationService
from ..math_solving.application.use_cases import (
    DeleteProblemUseCase,
    GetUserHistoryUseCase,
    SolveMathProblemUseCase,
)
from ..math_solving.domain.interfaces import AIService, MathSolverRepository
from ..math_solving.infrastructure.ai_service import OpenAIMathSolverService
from ..math_solving.infrastructure.repository import FirebaseMathSolverRepository


class Container:
    """Dependency injection container."""

    def __init__(self):
        self._instances = {}

    @lru_cache(maxsize=1)
    def auth_service(self) -> AuthenticationService:
        """Get authentication service instance."""
        if "auth_service" not in self._instances:
            self._instances["auth_service"] = FirebaseAuthenticationService()
        return self._instances["auth_service"]

    @lru_cache(maxsize=1)
    def ai_service(self) -> AIService:
        """Get AI service instance."""
        if "ai_service" not in self._instances:
            self._instances["ai_service"] = OpenAIMathSolverService()
        return self._instances["ai_service"]

    @lru_cache(maxsize=1)
    def math_solver_repository(self) -> MathSolverRepository:
        """Get math solver repository instance."""
        if "math_solver_repository" not in self._instances:
            self._instances["math_solver_repository"] = FirebaseMathSolverRepository()
        return self._instances["math_solver_repository"]

    @lru_cache(maxsize=1)
    def solve_math_problem_use_case(self) -> SolveMathProblemUseCase:
        """Get solve math problem use case instance."""
        if "solve_math_problem_use_case" not in self._instances:
            self._instances["solve_math_problem_use_case"] = SolveMathProblemUseCase(
                ai_service=self.ai_service(), repository=self.math_solver_repository()
            )
        return self._instances["solve_math_problem_use_case"]

    @lru_cache(maxsize=1)
    def get_user_history_use_case(self) -> GetUserHistoryUseCase:
        """Get user history use case instance."""
        if "get_user_history_use_case" not in self._instances:
            self._instances["get_user_history_use_case"] = GetUserHistoryUseCase(
                repository=self.math_solver_repository()
            )
        return self._instances["get_user_history_use_case"]

    @lru_cache(maxsize=1)
    def delete_problem_use_case(self) -> DeleteProblemUseCase:
        """Get delete problem use case instance."""
        if "delete_problem_use_case" not in self._instances:
            self._instances["delete_problem_use_case"] = DeleteProblemUseCase(
                repository=self.math_solver_repository()
            )
        return self._instances["delete_problem_use_case"]


# Global container instance
container = Container()
