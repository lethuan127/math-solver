import pytest
from unittest.mock import patch, MagicMock

from app.services.math_solver import MathSolver


class TestMathSolver:
    """Test cases for MathSolver service"""

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    @patch("app.services.math_solver.openai.AsyncOpenAI")
    def test_math_solver_initialization(self, mock_openai_class):
        """Test that MathSolver initializes correctly"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        solver = MathSolver()
        
        assert solver.client == mock_client
        assert solver.settings is not None