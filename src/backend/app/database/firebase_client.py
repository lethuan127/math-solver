import logging
from datetime import datetime
from typing import Any

import firebase_admin
from firebase_admin import auth, credentials, firestore, storage

from ..core.config import get_settings

logger = logging.getLogger(__name__)


class FirebaseClient:
    """Firebase integration client for authentication, database, and storage"""

    def __init__(self):
        self.settings = get_settings()
        self._initialize_firebase()
        self.db = firestore.client()
        self.bucket = storage.bucket()

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        if not firebase_admin._apps:
            try:
                # Initialize with service account credentials
                cred = credentials.Certificate(
                    {
                        "type": "service_account",
                        "project_id": self.settings.firebase_project_id,
                        "private_key": self.settings.firebase_private_key.replace(
                            "\\n", "\n"
                        ),
                        "client_email": self.settings.firebase_client_email,
                    }
                )
                firebase_admin.initialize_app(
                    cred, {"storageBucket": self.settings.firebase_storage_bucket}
                )
                logger.info("Firebase initialized successfully")
            except Exception as e:
                logger.error(f"Firebase initialization failed: {str(e)}")
                raise

    async def verify_token(self, token: str) -> dict[str, Any] | None:
        """Verify Firebase authentication token"""
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            return None

    async def save_solution(self, user_id: str, problem_data: dict[str, Any]) -> str:
        """Save math solution to Firestore"""
        try:
            doc_ref = (
                self.db.collection("users")
                .document(user_id)
                .collection("solutions")
                .document()
            )
            problem_data["created_at"] = datetime.utcnow()
            problem_data["updated_at"] = datetime.utcnow()
            doc_ref.set(problem_data)
            logger.info(f"Solution saved for user {user_id}")
            return doc_ref.id
        except Exception as e:
            logger.error(f"Failed to save solution: {str(e)}")
            raise

    async def get_user_history(
        self, user_id: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get user's solution history from Firestore"""
        try:
            docs = (
                self.db.collection("users")
                .document(user_id)
                .collection("solutions")
                .order_by("created_at", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream()
            )

            history = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                history.append(data)

            return history
        except Exception as e:
            logger.error(f"Failed to get user history: {str(e)}")
            raise

    async def delete_problem(self, user_id: str, problem_id: str) -> bool:
        """Delete a specific problem from user's history"""
        try:
            doc_ref = (
                self.db.collection("users")
                .document(user_id)
                .collection("solutions")
                .document(problem_id)
            )
            doc_ref.delete()
            logger.info(f"Problem {problem_id} deleted for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete problem: {str(e)}")
            raise

    async def upload_file(
        self, file_content: bytes, filename: str, user_id: str
    ) -> str:
        """Upload file to Firebase Storage"""
        try:
            blob = self.bucket.blob(f"uploads/{user_id}/{filename}")
            blob.upload_from_string(file_content)
            blob.make_public()
            logger.info(f"File {filename} uploaded for user {user_id}")
            return blob.public_url
        except Exception as e:
            logger.error(f"Failed to upload file: {str(e)}")
            raise
