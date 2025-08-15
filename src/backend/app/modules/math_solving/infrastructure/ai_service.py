"""AI service implementation for math solving."""

import base64
import logging

import openai
from fastapi import UploadFile

from ...shared.config import get_settings
from ..domain.entities import MathAnswer
from ..domain.interfaces import AIService

logger = logging.getLogger(__name__)


class OpenAIMathSolverService(AIService):
    """OpenAI-based implementation of math solving service."""

    def __init__(self):
        self.settings = get_settings()
        self.client = openai.AsyncOpenAI(api_key=self.settings.openai_api_key)

    async def solve_problem(self, image_file: UploadFile) -> MathAnswer:
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
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Solve this math problem"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{image_file.content_type};base64,{file_base64}"
                                },
                            },
                        ],
                    },
                ],
                text_format=MathAnswer,
            )

            answer = response.output_parsed

            return answer

        except Exception as e:
            logger.error(f"Error solving math problem: {str(e)}")
            # Return fallback response
            return MathAnswer(
                question="Math problem from uploaded image",
                answer_label=None,
                answer_value="Unable to solve problem",
                explanation=f"An error occurred: {str(e)}",
                steps=[],
                confidence=0.0,
            )
