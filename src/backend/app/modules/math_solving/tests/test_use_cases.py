"""Tests for math solving use cases."""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException, UploadFile

from ..application.use_cases import (
    DeleteProblemUseCase,
    GetUserHistoryUseCase,
    SolveMathProblemUseCase,
)
from ..domain.entities import MathAnswer, MathProblem, SolutionStep, User
from ..domain.interfaces import AIService, MathSolverRepository


class TestSolveMathProblemUseCase:
    """Test cases for SolveMathProblemUseCase."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_ai_service = Mock(spec=AIService)
        self.mock_repository = Mock(spec=MathSolverRepository)
        self.use_case = SolveMathProblemUseCase(
            ai_service=self.mock_ai_service, repository=self.mock_repository
        )

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful problem solving."""
        # Mock file upload
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test.png"
        mock_file.content_type = "image/png"

        # Mock user
        user = User(uid="user_123", email="test@example.com")

        # Mock AI service response
        mock_answer = MathAnswer(
            question="What is 2 + 2?",
            answer_label=None,
            answer_value="4",
            explanation="Simple addition",
            steps=[SolutionStep(1, "Add numbers", "2 + 2 = 4")],
            confidence=0.95,
        )
        self.mock_ai_service.solve_problem = AsyncMock(return_value=mock_answer)

        # Mock repository save
        self.mock_repository.save_problem = AsyncMock(return_value="problem_123")

        # Execute use case
        result = await self.use_case.execute(mock_file, user)

        # Verify result
        assert isinstance(result, MathProblem)
        assert result.id == "problem_123"
        assert result.question == "What is 2 + 2?"
        assert result.answer == mock_answer
        assert result.user_id == "user_123"
        assert result.file_name == "test.png"
        assert result.content_type == "image/png"
        assert isinstance(result.created_at, datetime)

        # Verify service calls
        self.mock_ai_service.solve_problem.assert_called_once_with(mock_file)
        self.mock_repository.save_problem.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_ai_service_failure(self):
        """Test handling AI service failure."""
        # Mock file and user
        mock_file = Mock(spec=UploadFile)
        user = User(uid="user_123")

        # Mock AI service failure
        self.mock_ai_service.solve_problem = AsyncMock(
            side_effect=Exception("AI service error")
        )

        # Execute use case should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await self.use_case.execute(mock_file, user)

        assert exc_info.value.status_code == 500
        assert "Solving failed" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_execute_repository_save_failure(self):
        """Test handling repository save failure (should not fail the request)."""
        # Mock file and user
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test.png"
        mock_file.content_type = "image/png"
        user = User(uid="user_123")

        # Mock AI service success
        mock_answer = MathAnswer(
            question="Test?",
            answer_label=None,
            answer_value="Test answer",
            explanation="Test explanation",
            steps=[],
            confidence=0.8,
        )
        self.mock_ai_service.solve_problem = AsyncMock(return_value=mock_answer)

        # Mock repository save failure
        self.mock_repository.save_problem = AsyncMock(
            side_effect=Exception("Database error")
        )

        # Execute use case should succeed (history saving is optional)
        result = await self.use_case.execute(mock_file, user)

        # Verify result (problem should be returned even if save failed)
        assert isinstance(result, MathProblem)
        assert result.id is None  # ID not set due to save failure
        assert result.answer == mock_answer


class TestGetUserHistoryUseCase:
    """Test cases for GetUserHistoryUseCase."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_repository = Mock(spec=MathSolverRepository)
        self.use_case = GetUserHistoryUseCase(repository=self.mock_repository)

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful history retrieval."""
        # Mock user
        user = User(uid="user_123")

        # Mock repository response
        mock_problems = [
            MathProblem(
                id="problem_1",
                question="What is 2 + 2?",
                answer=None,
                user_id="user_123",
                file_name="test1.png",
                content_type="image/png",
            ),
            MathProblem(
                id="problem_2",
                question="What is 3 + 3?",
                answer=None,
                user_id="user_123",
                file_name="test2.png",
                content_type="image/png",
            ),
        ]
        self.mock_repository.get_user_problems = AsyncMock(return_value=mock_problems)

        # Execute use case
        result = await self.use_case.execute(user, limit=10)

        # Verify result
        assert len(result) == 2
        assert all(isinstance(p, MathProblem) for p in result)

        # Verify repository call
        self.mock_repository.get_user_problems.assert_called_once_with("user_123", 10)

    @pytest.mark.asyncio
    async def test_execute_repository_failure(self):
        """Test handling repository failure."""
        # Mock user
        user = User(uid="user_123")

        # Mock repository failure
        self.mock_repository.get_user_problems = AsyncMock(
            side_effect=Exception("Database error")
        )

        # Execute use case should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await self.use_case.execute(user)

        assert exc_info.value.status_code == 500
        assert "Failed to retrieve history" in str(exc_info.value.detail)


class TestDeleteProblemUseCase:
    """Test cases for DeleteProblemUseCase."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_repository = Mock(spec=MathSolverRepository)
        self.use_case = DeleteProblemUseCase(repository=self.mock_repository)

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful problem deletion."""
        # Mock user
        user = User(uid="user_123")

        # Mock repository success
        self.mock_repository.delete_problem = AsyncMock(return_value=True)

        # Execute use case
        result = await self.use_case.execute("problem_123", user)

        # Verify result
        assert result is True

        # Verify repository call
        self.mock_repository.delete_problem.assert_called_once_with(
            "problem_123", "user_123"
        )

    @pytest.mark.asyncio
    async def test_execute_problem_not_found(self):
        """Test handling problem not found."""
        # Mock user
        user = User(uid="user_123")

        # Mock repository returning False (not found)
        self.mock_repository.delete_problem = AsyncMock(return_value=False)

        # Execute use case should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await self.use_case.execute("problem_123", user)

        assert exc_info.value.status_code == 404
        assert "Problem not found or access denied" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_execute_repository_failure(self):
        """Test handling repository failure."""
        # Mock user
        user = User(uid="user_123")

        # Mock repository failure
        self.mock_repository.delete_problem = AsyncMock(
            side_effect=Exception("Database error")
        )

        # Execute use case should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await self.use_case.execute("problem_123", user)

        assert exc_info.value.status_code == 500
        assert "Failed to delete problem" in str(exc_info.value.detail)
