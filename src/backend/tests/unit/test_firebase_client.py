from unittest.mock import MagicMock, patch

import pytest

from app.database.firebase_client import FirebaseClient


class TestFirebaseClient:
    @patch("firebase_admin.storage.bucket")
    @patch("firebase_admin.firestore.client")
    @patch("firebase_admin.initialize_app")
    @patch("firebase_admin.credentials.Certificate")
    def setup_method(self, method, mock_cert, mock_init, mock_firestore, mock_bucket):
        self.client = FirebaseClient()

    @patch("firebase_admin.auth.verify_id_token")
    @pytest.mark.asyncio
    async def test_verify_valid_token(self, mock_verify):
        mock_verify.return_value = {"uid": "test_user", "email": "test@example.com"}

        result = await self.client.verify_token("valid_token")

        assert result["uid"] == "test_user"
        assert result["email"] == "test@example.com"

    @patch("firebase_admin.auth.verify_id_token")
    @pytest.mark.asyncio
    async def test_verify_invalid_token(self, mock_verify):
        mock_verify.side_effect = Exception("Invalid token")

        result = await self.client.verify_token("invalid_token")

        assert result is None

    @pytest.mark.asyncio
    async def test_save_solution(self):
        # Mock the document reference
        mock_doc = MagicMock()
        mock_doc.id = "test_doc_id"
        
        # Setup the chain of mocks for the Firestore operations
        self.client.db.collection.return_value.document.return_value.collection.return_value.document.return_value = mock_doc

        problem_data = {"text": "2 + 2 = ?", "solution": "4"}

        result = await self.client.save_solution("test_user", problem_data)

        assert result == "test_doc_id"
        mock_doc.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_history(self):
        # Mock the document results
        mock_docs = [MagicMock(), MagicMock()]
        mock_docs[0].to_dict.return_value = {
            "text": "Problem 1",
            "solution": "Answer 1",
        }
        mock_docs[0].id = "doc1"
        mock_docs[1].to_dict.return_value = {
            "text": "Problem 2",
            "solution": "Answer 2",
        }
        mock_docs[1].id = "doc2"

        # Setup the chain of mocks for the Firestore query
        self.client.db.collection.return_value.document.return_value.collection.return_value.order_by.return_value.limit.return_value.stream.return_value = mock_docs

        result = await self.client.get_user_history("test_user")

        assert len(result) == 2
        assert result[0]["id"] == "doc1"
        assert result[1]["id"] == "doc2"
