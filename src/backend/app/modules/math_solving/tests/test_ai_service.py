"""Tests for AI service implementation."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import UploadFile

from ..domain.entities import MathAnswer
from ..infrastructure.ai_service import OpenAIMathSolverService


class TestOpenAIMathSolverService:
    """Test cases for OpenAI math solver service."""

    @patch("app.modules.math_solving.infrastructure.ai_service.get_settings")
    @patch("app.modules.math_solving.infrastructure.ai_service.openai.AsyncOpenAI")
    def setup_method(self, mock_openai_class, mock_get_settings):
        """Set up test fixtures."""
        # Mock settings
        mock_settings = Mock()
        mock_settings.openai_api_key = "test-api-key"
        mock_get_settings.return_value = mock_settings

        # Mock OpenAI client
        self.mock_openai_client = Mock()
        mock_openai_class.return_value = self.mock_openai_client

        self.service = OpenAIMathSolverService()

    @pytest.mark.asyncio
    async def test_solve_problem_success(self):
        """Test successful problem solving."""
        # Mock file upload
        mock_file = Mock(spec=UploadFile)
        mock_file.read = AsyncMock(return_value=b"fake_image_data")
        mock_file.content_type = "image/png"

        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[
            0
        ].message.content = "The answer is 4. Step 1: Add 2 + 2 = 4"

        self.mock_openai_client.chat.completions.create = AsyncMock(
            return_value=mock_response
        )

        # Execute
        result = await self.service.solve_problem(mock_file)

        # Verify result
        assert isinstance(result, MathAnswer)
        assert result.question == "Math problem from uploaded image"
        assert result.answer_value is not None
        assert result.explanation is not None
        assert len(result.steps) > 0
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_solve_problem_openai_failure(self):
        """Test handling OpenAI API failure."""
        # Mock file upload
        mock_file = Mock(spec=UploadFile)
        mock_file.read = AsyncMock(return_value=b"fake_image_data")
        mock_file.content_type = "image/png"

        # Mock OpenAI failure
        self.mock_openai_client.chat.completions.create = AsyncMock(
            side_effect=Exception("OpenAI API error")
        )

        # Execute
        result = await self.service.solve_problem(mock_file)

        # Verify fallback response
        assert isinstance(result, MathAnswer)
        assert result.answer_value == "Unable to solve problem"
        assert "An error occurred" in result.explanation
        assert result.confidence == 0.0

    @pytest.mark.asyncio
    async def test_solve_problem_file_read_failure(self):
        """Test handling file read failure."""
        # Mock file upload with read failure
        mock_file = Mock(spec=UploadFile)
        mock_file.read = AsyncMock(side_effect=Exception("File read error"))
        mock_file.content_type = "image/png"

        # Execute
        result = await self.service.solve_problem(mock_file)

        # Verify fallback response
        assert isinstance(result, MathAnswer)
        assert result.answer_value == "Unable to solve problem"
        assert "An error occurred" in result.explanation
        assert result.confidence == 0.0

    @patch("app.modules.math_solving.infrastructure.ai_service.base64.b64encode")
    @pytest.mark.asyncio
    async def test_solve_problem_base64_encoding(self, mock_b64encode):
        """Test that file content is properly base64 encoded."""
        # Mock file upload
        mock_file = Mock(spec=UploadFile)
        mock_file.read = AsyncMock(return_value=b"fake_image_data")
        mock_file.content_type = "image/png"

        # Mock base64 encoding
        mock_b64encode.return_value.decode.return_value = "encoded_image_data"

        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        self.mock_openai_client.chat.completions.create = AsyncMock(
            return_value=mock_response
        )

        # Execute
        await self.service.solve_problem(mock_file)

        # Verify base64 encoding was called
        mock_b64encode.assert_called_once_with(b"fake_image_data")

        # Verify OpenAI was called with correct parameters
        call_args = self.mock_openai_client.chat.completions.create.call_args
        assert call_args is not None
        assert "model" in call_args.kwargs
        assert "messages" in call_args.kwargs
