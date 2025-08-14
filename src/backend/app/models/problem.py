from pydantic import BaseModel


class ProblemRequest(BaseModel):
    image_data: str  # Base64 encoded image


class SolutionStep(BaseModel):
    step_number: int
    description: str
    calculation: str | None = None


class MathSolution(BaseModel):
    solution: str
    steps: list[SolutionStep]
    explanation: str
    confidence: float


class ProblemResponse(BaseModel):
    original_text: str
    solution: str
    steps: list[SolutionStep]
    explanation: str
