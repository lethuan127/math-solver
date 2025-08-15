"""API endpoints for math solving module."""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ...auth.domain.entities import User
from ...shared.container import container
from ..application.dto import (
    DeleteProblemResponseDTO,
    MathAnswerDTO,
    ProblemHistoryItemDTO,
    ProblemResponseDTO,
    SolutionStepDTO,
    UserHistoryResponseDTO,
)
from ..domain.entities import MathProblem

logger = logging.getLogger(__name__)
router = APIRouter()


def convert_problem_to_response_dto(problem: MathProblem) -> ProblemResponseDTO:
    """Convert domain entity to response DTO."""
    if not problem.answer:
        raise ValueError("Problem must have an answer")

    return ProblemResponseDTO(
        question=problem.question,
        answer=MathAnswerDTO(
            question=problem.answer.question,
            answer_label=problem.answer.answer_label,
            answer_value=problem.answer.answer_value,
            explanation=problem.answer.explanation,
            steps=[
                SolutionStepDTO(
                    step_number=step.step_number,
                    description=step.description,
                    calculation=step.calculation,
                )
                for step in problem.answer.steps
            ],
            confidence=problem.answer.confidence,
        ),
    )


def convert_problem_to_history_dto(problem: MathProblem) -> ProblemHistoryItemDTO:
    """Convert domain entity to history DTO."""
    if not problem.answer or not problem.id or not problem.created_at:
        raise ValueError("Problem must have answer, id, and created_at")

    return ProblemHistoryItemDTO(
        id=problem.id,
        question=problem.question,
        answer=MathAnswerDTO(
            question=problem.answer.question,
            answer_label=problem.answer.answer_label,
            answer_value=problem.answer.answer_value,
            explanation=problem.answer.explanation,
            steps=[
                SolutionStepDTO(
                    step_number=step.step_number,
                    description=step.description,
                    calculation=step.calculation,
                )
                for step in problem.answer.steps
            ],
            confidence=problem.answer.confidence,
        ),
        file_name=problem.file_name,
        created_at=problem.created_at,
    )


@router.post("/solve", response_model=ProblemResponseDTO)
async def solve_problem(
    file: UploadFile = File(...),
    current_user: User = Depends(container.auth_service().get_current_user),
) -> ProblemResponseDTO:
    """Process and solve math problem (requires authentication)."""
    try:
        logger.info(f"Processing math problem for user: {current_user.uid}")

        use_case = container.solve_math_problem_use_case()
        problem = await use_case.execute(file, current_user)

        return convert_problem_to_response_dto(problem)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Solving failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Solving failed: {str(e)}") from e


@router.get("/history", response_model=UserHistoryResponseDTO)
async def get_user_history(
    current_user: User = Depends(container.auth_service().get_current_user),
) -> UserHistoryResponseDTO:
    """Get user's problem solving history (requires authentication)."""
    try:
        logger.info(f"Retrieving history for user: {current_user.uid}")

        use_case = container.get_user_history_use_case()
        problems = await use_case.execute(current_user)

        history_items = [
            convert_problem_to_history_dto(problem)
            for problem in problems
            if problem.answer and problem.id and problem.created_at
        ]

        return UserHistoryResponseDTO(
            history=history_items,
            user_id=current_user.uid,
            total_problems=len(history_items),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve history: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve history: {str(e)}"
        ) from e


@router.delete("/history/{problem_id}", response_model=DeleteProblemResponseDTO)
async def delete_problem(
    problem_id: str,
    current_user: User = Depends(container.auth_service().get_current_user),
) -> DeleteProblemResponseDTO:
    """Delete a specific problem from history (requires authentication)."""
    try:
        logger.info(f"Deleting problem {problem_id} for user: {current_user.uid}")

        use_case = container.delete_problem_use_case()
        await use_case.execute(problem_id, current_user)

        return DeleteProblemResponseDTO(
            message="Problem deleted successfully",
            problem_id=problem_id,
            user_id=current_user.uid,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete problem: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete problem: {str(e)}"
        ) from e
