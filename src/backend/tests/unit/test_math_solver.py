from unittest.mock import MagicMock, patch

import pytest

from app.models.problem import ProblemRequest
from app.services.math_solver import MathSolver


class TestMathSolver:
    def setup_method(self):
        # We'll mock OpenAI in each test method
        pass

    @patch("app.services.math_solver.openai.AsyncOpenAI")
    @pytest.mark.asyncio
    async def test_solve_basic_arithmetic(self, mock_openai_class):
        # Mock OpenAI client and response
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Create solver with mocked client
        solver = MathSolver()
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"solution": "4", "steps": [{"step_number": 1, "description": "Add 2 + 2", "calculation": "2 + 2 = 4"}], "explanation": "Simple addition", "confidence": 0.95}'
        
        # Mock the async create method
        async def mock_create(*args, **kwargs):
            return mock_response
        
        mock_client.chat.completions.create = mock_create

        problem_text = "2 + 2 = ?"

        result = await solver.solve(problem_text)

        assert result.solution == "4"
        assert "addition" in result.explanation.lower()
        assert len(result.steps) > 0

    def test_classify_problem_type(self):
        # Create a solver for non-async tests
        solver = MathSolver.__new__(MathSolver)  # Create without calling __init__
        
        # Test different problem classifications
        assert solver.classify_problem("2 + 2") == "arithmetic"
        assert solver.classify_problem("x^2 + 5x + 6 = 0") == "algebra"
        assert solver.classify_problem("∫ x dx") == "calculus"
        assert solver.classify_problem("sin(30°)") == "trigonometry"

    def test_format_solution_steps(self):
        # Create a solver for non-async tests
        solver = MathSolver.__new__(MathSolver)  # Create without calling __init__
        
        steps = ["Step 1: 2 + 2", "Step 2: = 4"]
        formatted = solver.format_steps(steps)

        assert isinstance(formatted, list)
        assert len(formatted) == 2
        assert "Step 1" in formatted[0]
