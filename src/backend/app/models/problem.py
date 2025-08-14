from pydantic import BaseModel, Field
from typing import Optional


class ProblemRequest(BaseModel):
    image_data: str  # Base64 encoded image

class SolutionStep(BaseModel):
    step_number: int
    description: str
    calculation: str | None = None

class Answer(BaseModel):
    question: str = Field(..., title="Question", description="The question to be answered")
    answer_label: Optional[str] = Field(None, title="Answer Label", description="The label of the answer (e.g., A, B, C, D, 1, 2, 3, 4, etc.)")
    answer_value: str = Field(..., title="Answer Value")
    explanation: str = Field(..., title="Explanation", description="The explanation of the answer")
    steps: list[SolutionStep] = Field(..., title="Steps", description="The steps to solve the problem")
    confidence: float = Field(..., title="Confidence", description="The confidence in the answer (0.0 to 1.0)")

class ProblemResponse(BaseModel):
    question: str = Field(..., title="Question", description="The question to be answered")
    answer: Answer = Field(..., title="Answer", description="The answer to the question")