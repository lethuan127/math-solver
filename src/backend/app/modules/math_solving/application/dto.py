"""Data Transfer Objects for math solving module."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SolutionStepDTO(BaseModel):
    """DTO for a solution step."""

    step_number: int
    description: str
    calculation: Optional[str] = None


class MathAnswerDTO(BaseModel):
    """DTO for a math answer."""

    question: str = Field(
        ..., title="Question", description="The question to be answered"
    )
    answer_label: Optional[str] = Field(
        None,
        title="Answer Label",
        description="The label of the answer (e.g., A, B, C, D, 1, 2, 3, 4, etc.)",
    )
    answer_value: str = Field(..., title="Answer Value")
    explanation: str = Field(
        ..., title="Explanation", description="The explanation of the answer"
    )
    steps: list[SolutionStepDTO] = Field(
        ..., title="Steps", description="The steps to solve the problem"
    )
    confidence: float = Field(
        ..., title="Confidence", description="The confidence in the answer (0.0 to 1.0)"
    )


class ProblemResponseDTO(BaseModel):
    """DTO for problem response."""

    question: str = Field(
        ..., title="Question", description="The question to be answered"
    )
    answer: MathAnswerDTO = Field(
        ..., title="Answer", description="The answer to the question"
    )


class ProblemHistoryItemDTO(BaseModel):
    """DTO for a problem in user's history."""

    id: str
    question: str
    answer: MathAnswerDTO
    file_name: str
    created_at: datetime


class UserHistoryResponseDTO(BaseModel):
    """DTO for user history response."""

    history: list[ProblemHistoryItemDTO]
    user_id: str
    total_problems: int


class DeleteProblemResponseDTO(BaseModel):
    """DTO for delete problem response."""

    message: str
    problem_id: str
    user_id: str
