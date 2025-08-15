"""AI service implementation for math solving."""

import base64
import logging
from typing import Optional

import openai
from fastapi import UploadFile
from pydantic import BaseModel, Field

from ...shared.config import get_settings
from ..domain.entities import MathAnswer as DomainMathAnswer
from ..domain.interfaces import AIService

logger = logging.getLogger(__name__)



class SolutionStep(BaseModel):
    """A single step in solving a math problem."""

    step_number: int = Field(None, title="Step Number", description="The step number of the solution")
    description: str = Field(None, title="Description", description="The description of the solution")
    calculation: Optional[str] = Field(None, title="Calculation", description="The calculation of the solution")


class MathAnswer(BaseModel):
    """The answer to a math problem."""

    question: str = Field(None, title="Question", description="The question of the math problem")
    answer_label: Optional[str] = Field(None, title="Answer Label", description="The label of the answer")
    answer_value: str = Field(None, title="Answer Value", description="The value of the answer")
    explanation: str = Field(None, title="Explanation", description="The explanation of the answer")
    steps: list[SolutionStep] = Field(None, title="Steps", description="The steps of the solution")
    confidence: float = Field(None, title="Confidence", description="The confidence of the answer")


class OpenAIMathSolverService(AIService):
    """OpenAI-based implementation of math solving service."""

    def __init__(self):
        self.settings = get_settings()
        self.client = openai.AsyncOpenAI(api_key=self.settings.openai_api_key)

    async def solve_problem(self, image_file: UploadFile) -> DomainMathAnswer:
        """
        Solve math problem using OpenAI GPT with vision capabilities.

        Args:
            image_file: The uploaded image file containing the math problem

        Returns:
            MathAnswer: The solved problem with steps and explanation

        Raises:
            Exception: If solving fails
        """
        try:
            file_content = await image_file.read()
            file_base64 = base64.b64encode(file_content).decode("utf-8")

            system_prompt = """
            You are a mathematics tutor helping students solve homework problems.
            Given a math problem, provide:
            1. The final answer
            2. Step-by-step solution
            3. Clear explanation of concepts used

            Be thorough but concise. Show all work clearly.
            """

            # Note: This is using a hypothetical API structure
            # In reality, you'd need to adapt this to the actual OpenAI API
            response = await self.client.responses.parse(
                model="gpt-5",
                input=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "Solve this math problem"},
                            {
                                "type": "input_image",
                                "image_url": f"data:{image_file.content_type};base64,{file_base64}"
                            },
                        ],
                    },
                ],
                text_format=MathAnswer,
            )

            answer = response.output_parsed

            return DomainMathAnswer(
                question=answer.question,
                answer_label=answer.answer_label,
                answer_value=answer.answer_value,
                explanation=answer.explanation,
                steps=[SolutionStep(
                    step_number=step.step_number,
                    description=step.description,
                    calculation=step.calculation,
                ) for step in answer.steps],
                confidence=answer.confidence,
            )

        except Exception as e:
            logger.error(f"Error solving math problem: {str(e)}")
            # Return fallback response
            return DomainMathAnswer(
                question="Math problem from uploaded image",
                answer_label=None,
                answer_value="Unable to solve problem",
                explanation=f"An error occurred: {str(e)}",
                steps=[],
                confidence=0.0,
            )
