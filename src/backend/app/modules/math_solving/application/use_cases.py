"""Use cases for math solving module."""

import logging
from datetime import datetime

from fastapi import HTTPException, UploadFile

from ..domain.entities import MathProblem, User
from ..domain.interfaces import AIService, MathSolverRepository

logger = logging.getLogger(__name__)


class SolveMathProblemUseCase:
    """Use case for solving a math problem from an uploaded image."""

    def __init__(self, ai_service: AIService, repository: MathSolverRepository):
        self.ai_service = ai_service
        self.repository = repository

    async def execute(self, file: UploadFile, user: User) -> MathProblem:
        """
        Solve a math problem and optionally save it to user's history.

        Args:
            file: The uploaded image file containing the math problem
            user: The authenticated user

        Returns:
            MathProblem: The solved problem with answer

        Raises:
            HTTPException: If solving fails
        """
        try:
            logger.info(f"Processing math problem for user: {user.uid}")

            # Solve the problem using AI service
            answer = await self.ai_service.solve_problem(file)

            # Create problem entity
            problem = MathProblem(
                id=None,
                question=answer.question,
                answer=answer,
                user_id=user.uid,
                file_name=file.filename or "unknown",
                content_type=file.content_type or "unknown",
                created_at=datetime.utcnow(),
            )

            # Save to user's history
            try:
                problem_id = await self.repository.save_problem(problem)
                problem.id = problem_id
                logger.info(f"Problem saved to history with ID: {problem_id}")
            except Exception as save_error:
                logger.warning(f"Failed to save problem to history: {str(save_error)}")
                # Don't fail the request if history saving fails

            return problem

        except Exception as e:
            logger.error(f"Solving failed: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Solving failed: {str(e)}"
            ) from e


class GetUserHistoryUseCase:
    """Use case for retrieving user's problem history."""

    def __init__(self, repository: MathSolverRepository):
        self.repository = repository

    async def execute(self, user: User, limit: int = 50) -> list[MathProblem]:
        """
        Get user's problem solving history.

        Args:
            user: The authenticated user
            limit: Maximum number of problems to return

        Returns:
            List[MathProblem]: List of user's solved problems
        """
        try:
            logger.info(f"Retrieving history for user: {user.uid}")
            return await self.repository.get_user_problems(user.uid, limit)
        except Exception as e:
            logger.error(f"Failed to retrieve history: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to retrieve history: {str(e)}"
            ) from e


class DeleteProblemUseCase:
    """Use case for deleting a problem from user's history."""

    def __init__(self, repository: MathSolverRepository):
        self.repository = repository

    async def execute(self, problem_id: str, user: User) -> bool:
        """
        Delete a problem from user's history.

        Args:
            problem_id: ID of the problem to delete
            user: The authenticated user

        Returns:
            bool: True if deleted successfully

        Raises:
            HTTPException: If deletion fails or problem not found
        """
        try:
            logger.info(f"Deleting problem {problem_id} for user: {user.uid}")

            deleted = await self.repository.delete_problem(problem_id, user.uid)
            if not deleted:
                raise HTTPException(
                    status_code=404, detail="Problem not found or access denied"
                )

            return deleted

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete problem: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to delete problem: {str(e)}"
            ) from e
