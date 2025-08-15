"""Domain entities for math solving module."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SolutionStep:
    """A single step in solving a math problem."""

    step_number: int
    description: str
    calculation: Optional[str] = None


@dataclass
class MathAnswer:
    """The answer to a math problem."""

    question: str
    answer_label: Optional[str]
    answer_value: str
    explanation: str
    steps: list[SolutionStep]
    confidence: float

    def __post_init__(self):
        """Validate confidence score."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


@dataclass
class MathProblem:
    """A math problem to be solved."""

    id: Optional[str]
    question: str
    answer: Optional[MathAnswer]
    user_id: str
    file_name: str
    content_type: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class User:
    """A user of the math solver system."""

    uid: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    created_at: Optional[datetime] = None
