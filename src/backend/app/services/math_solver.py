import json
import logging
import os

import openai

from ..models.problem import MathSolution, SolutionStep


class MathSolver:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def solve(self, problem_text: str) -> MathSolution:
        """
        Solve math problem using OpenAI GPT
        """
        try:
            system_prompt = """
            You are a mathematics tutor helping students solve homework problems.
            Given a math problem, provide:
            1. The final answer
            2. Step-by-step solution
            3. Clear explanation of concepts used

            Format your response as JSON with this structure:
            {
                "solution": "final answer",
                "steps": [
                    {"step_number": 1, "description": "step description", "calculation": "calculation if any"},
                    ...
                ],
                "explanation": "explanation of concepts and methods used",
                "confidence": 0.95
            }

            Be thorough but concise. Show all work clearly.
            """

            user_prompt = f"Solve this math problem: {problem_text}"

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=1500,
            )

            # Parse JSON response
            response_text = response.choices[0].message.content
            solution_data = json.loads(response_text)

            # Convert to MathSolution model
            steps = [
                SolutionStep(
                    step_number=step["step_number"],
                    description=step["description"],
                    calculation=step.get("calculation"),
                )
                for step in solution_data["steps"]
            ]

            return MathSolution(
                solution=solution_data["solution"],
                steps=steps,
                explanation=solution_data["explanation"],
                confidence=solution_data.get("confidence", 0.8),
            )

        except Exception as e:
            logging.error(f"Error solving math problem: {str(e)}")
            # Fallback response
            return MathSolution(
                solution="Unable to solve problem",
                steps=[
                    SolutionStep(
                        step_number=1,
                        description="Error occurred during solving",
                        calculation=None,
                    )
                ],
                explanation=f"An error occurred: {str(e)}",
                confidence=0.0,
            )

    def classify_problem(self, problem_text: str) -> str:
        """
        Classify the type of math problem
        """
        problem_lower = problem_text.lower()
        
        # Check for calculus first (most specific)
        if any(term in problem_lower for term in ['∫', 'derivative', 'integral', 'limit']):
            return "calculus"
        # Check for trigonometry
        elif any(term in problem_lower for term in ['sin', 'cos', 'tan', '°', 'π']):
            return "trigonometry"
        # Check for algebra (variables and equations)
        elif any(term in problem_lower for term in ['x^', 'x²', 'x2', 'solve for']) or ('x' in problem_lower and '=' in problem_text):
            return "algebra"
        # Check for basic arithmetic
        elif any(op in problem_text for op in ['+', '-', '*', '/', '×', '÷']):
            return "arithmetic"
        else:
            return "general"
    
    def format_steps(self, steps: list[str]) -> list[str]:
        """
        Format solution steps for display
        """
        return [step.strip() for step in steps if step.strip()]
