"""Repository implementation for math solving module."""

import logging
import uuid
from datetime import datetime
from typing import Optional

from ...shared.database.firebase_client import FirebaseClient
from ..domain.entities import MathProblem
from ..domain.interfaces import MathSolverRepository

logger = logging.getLogger(__name__)


class FirebaseMathSolverRepository(MathSolverRepository):
    """Firebase implementation of math solver repository."""

    def __init__(self):
        self._firebase_client: Optional[FirebaseClient] = None

    def get_firebase_client(self) -> FirebaseClient:
        """Get Firebase client instance (lazy initialization)."""
        if self._firebase_client is None:
            self._firebase_client = FirebaseClient()
        return self._firebase_client

    async def save_problem(self, problem: MathProblem) -> str:
        """
        Save a math problem to Firebase and return its ID.

        Args:
            problem: The problem to save

        Returns:
            str: The generated problem ID
        """
        try:
            client = self.get_firebase_client()

            # Generate ID if not provided
            problem_id = problem.id or str(uuid.uuid4())

            problem_data = {
                "question": problem.question,
                "answer": {
                    "question": problem.answer.question,
                    "answer_label": problem.answer.answer_label,
                    "answer_value": problem.answer.answer_value,
                    "explanation": problem.answer.explanation,
                    "steps": [
                        {
                            "step_number": step.step_number,
                            "description": step.description,
                            "calculation": step.calculation,
                        }
                        for step in problem.answer.steps
                    ],
                    "confidence": problem.answer.confidence,
                }
                if problem.answer
                else None,
                "user_id": problem.user_id,
                "file_name": problem.file_name,
                "content_type": problem.content_type,
                "created_at": problem.created_at or datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            await client.save_solution(problem.user_id, problem_data)
            return problem_id

        except Exception as e:
            logger.error(f"Failed to save problem: {str(e)}")
            raise

    async def get_problem(self, problem_id: str, user_id: str) -> Optional[MathProblem]:
        """
        Get a specific problem by ID for a user.

        Args:
            problem_id: The problem ID
            user_id: The user ID

        Returns:
            Optional[MathProblem]: The problem if found, None otherwise
        """
        try:
            client = self.get_firebase_client()
            # This would need to be implemented in FirebaseClient
            # For now, return None as placeholder
            return None

        except Exception as e:
            logger.error(f"Failed to get problem {problem_id}: {str(e)}")
            return None

    async def get_user_problems(
        self, user_id: str, limit: int = 50
    ) -> list[MathProblem]:
        """
        Get all problems for a user.

        Args:
            user_id: The user ID
            limit: Maximum number of problems to return

        Returns:
            List[MathProblem]: List of user's problems
        """
        try:
            client = self.get_firebase_client()
            # This would need to be implemented in FirebaseClient
            # For now, return empty list as placeholder
            return []

        except Exception as e:
            logger.error(f"Failed to get problems for user {user_id}: {str(e)}")
            return []

    async def delete_problem(self, problem_id: str, user_id: str) -> bool:
        """
        Delete a problem.

        Args:
            problem_id: The problem ID
            user_id: The user ID

        Returns:
            bool: True if deleted, False if not found
        """
        try:
            client = self.get_firebase_client()
            # This would need to be implemented in FirebaseClient
            # For now, return False as placeholder
            return False

        except Exception as e:
            logger.error(f"Failed to delete problem {problem_id}: {str(e)}")
            return False
