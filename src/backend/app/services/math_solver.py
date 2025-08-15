import base64
import logging

from fastapi import UploadFile
import openai

from ..models.problem import ProblemResponse
from ..core.config import get_settings


class MathSolver:
    def __init__(self):
        self.settings = get_settings()
        self.client = openai.AsyncOpenAI(api_key=self.settings.openai_api_key)

    async def solve(self, file: UploadFile) -> ProblemResponse:
        """
        Solve math problem using OpenAI GPT
        """
        try:
            file_content = await file.read()
            file_base64 = base64.b64encode(file_content).decode("utf-8")
    
            system_prompt = """
            You are a mathematics tutor helping students solve homework problems.
            Given a math problem, provide:
            1. The final answer
            2. Step-by-step solution
            3. Clear explanation of concepts used

            Be thorough but concise. Show all work clearly.
            """

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
                            { "type": "input_text", "text": "Solve this math problem" },
                            {
                                "type": "input_image",
                                "image_url": f"data:{file.content_type};base64,{file_base64}"
                            },
                        ],
                    }
                ],
                text_format=ProblemResponse
            )

            solution = response.output_parsed
            return solution

        except Exception as e:
            logging.error(f"Error solving math problem: {str(e)}")
            # Fallback response
            return ProblemResponse(
                solution="Unable to solve problem",
                explanation=f"An error occurred: {str(e)}",
                confidence=0.0,
            )