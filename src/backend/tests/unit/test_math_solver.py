from unittest.mock import MagicMock, patch

import pytest

from app.models.problem import MathProblem
from app.services.math_solver import MathSolver


class TestMathSolver:
    def setup_method(self):
        self.solver = MathSolver()

    @patch("openai.ChatCompletion.acreate")
    @pytest.mark.asyncio
    async def test_solve_basic_arithmetic(self, mock_openai):
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[
            0
        ].message.content = '{"solution": "4", "steps": ["2 + 2", "= 4"], "explanation": "Simple addition"}'
        mock_openai.return_value = mock_response

        problem = MathProblem(text="2 + 2 = ?", problem_type="arithmetic")

        result = await self.solver.solve(problem)

        assert result.solution == "4"
        assert "addition" in result.explanation.lower()
        assert len(result.steps) > 0

    def test_classify_problem_type(self):
        # Test different problem classifications
        assert self.solver.classify_problem("2 + 2") == "arithmetic"
        assert self.solver.classify_problem("x^2 + 5x + 6 = 0") == "algebra"
        assert self.solver.classify_problem("∫ x dx") == "calculus"
        assert self.solver.classify_problem("sin(30°)") == "trigonometry"

    def test_format_solution_steps(self):
        steps = ["Step 1: 2 + 2", "Step 2: = 4"]
        formatted = self.solver.format_steps(steps)

        assert isinstance(formatted, list)
        assert len(formatted) == 2
        assert "Step 1" in formatted[0]
