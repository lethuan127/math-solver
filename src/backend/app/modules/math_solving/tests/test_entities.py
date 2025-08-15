"""Tests for math solving domain entities."""

from datetime import datetime

import pytest

from ..domain.entities import MathAnswer, MathProblem, SolutionStep, User


class TestSolutionStep:
    """Test cases for SolutionStep entity."""

    def test_solution_step_creation(self):
        """Test creating a solution step."""
        step = SolutionStep(
            step_number=1,
            description="Add the numbers together",
            calculation="2 + 2 = 4",
        )

        assert step.step_number == 1
        assert step.description == "Add the numbers together"
        assert step.calculation == "2 + 2 = 4"

    def test_solution_step_without_calculation(self):
        """Test creating a solution step without calculation."""
        step = SolutionStep(step_number=1, description="Identify the problem type")

        assert step.step_number == 1
        assert step.description == "Identify the problem type"
        assert step.calculation is None


class TestMathAnswer:
    """Test cases for MathAnswer entity."""

    def test_math_answer_creation(self):
        """Test creating a math answer."""
        steps = [SolutionStep(1, "Add the numbers", "2 + 2 = 4")]

        answer = MathAnswer(
            question="What is 2 + 2?",
            answer_label="A",
            answer_value="4",
            explanation="Simple addition",
            steps=steps,
            confidence=0.95,
        )

        assert answer.question == "What is 2 + 2?"
        assert answer.answer_label == "A"
        assert answer.answer_value == "4"
        assert answer.explanation == "Simple addition"
        assert len(answer.steps) == 1
        assert answer.confidence == 0.95

    def test_math_answer_confidence_validation(self):
        """Test that confidence score is validated."""
        steps = [SolutionStep(1, "Test", "test")]

        # Test invalid confidence > 1.0
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            MathAnswer(
                question="Test?",
                answer_label=None,
                answer_value="test",
                explanation="test",
                steps=steps,
                confidence=1.5,
            )

        # Test invalid confidence < 0.0
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            MathAnswer(
                question="Test?",
                answer_label=None,
                answer_value="test",
                explanation="test",
                steps=steps,
                confidence=-0.1,
            )

    def test_math_answer_without_label(self):
        """Test creating a math answer without answer label."""
        steps = [SolutionStep(1, "Solve", "x = 5")]

        answer = MathAnswer(
            question="What is x?",
            answer_label=None,
            answer_value="5",
            explanation="Direct solution",
            steps=steps,
            confidence=0.8,
        )

        assert answer.answer_label is None
        assert answer.answer_value == "5"


class TestMathProblem:
    """Test cases for MathProblem entity."""

    def test_math_problem_creation(self):
        """Test creating a math problem."""
        steps = [SolutionStep(1, "Add", "2 + 2 = 4")]
        answer = MathAnswer(
            question="What is 2 + 2?",
            answer_label=None,
            answer_value="4",
            explanation="Simple addition",
            steps=steps,
            confidence=0.95,
        )

        created_at = datetime.utcnow()
        problem = MathProblem(
            id="problem_123",
            question="What is 2 + 2?",
            answer=answer,
            user_id="user_456",
            file_name="math.png",
            content_type="image/png",
            created_at=created_at,
        )

        assert problem.id == "problem_123"
        assert problem.question == "What is 2 + 2?"
        assert problem.answer == answer
        assert problem.user_id == "user_456"
        assert problem.file_name == "math.png"
        assert problem.content_type == "image/png"
        assert problem.created_at == created_at
        assert problem.updated_at is None

    def test_math_problem_without_answer(self):
        """Test creating a math problem without answer."""
        problem = MathProblem(
            id=None,
            question="What is x?",
            answer=None,
            user_id="user_123",
            file_name="problem.jpg",
            content_type="image/jpeg",
        )

        assert problem.id is None
        assert problem.answer is None
        assert problem.created_at is None


class TestUser:
    """Test cases for User entity."""

    def test_user_creation(self):
        """Test creating a user."""
        created_at = datetime.utcnow()
        user = User(
            uid="user_123",
            email="test@example.com",
            display_name="Test User",
            created_at=created_at,
        )

        assert user.uid == "user_123"
        assert user.email == "test@example.com"
        assert user.display_name == "Test User"
        assert user.created_at == created_at
