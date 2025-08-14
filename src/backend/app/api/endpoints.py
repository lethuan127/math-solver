import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..database.firebase_client import FirebaseClient
from ..models.problem import ProblemRequest, ProblemResponse
from ..services.image_processor import ImageProcessor
from ..services.math_solver import MathSolver

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
image_processor = ImageProcessor()
math_solver = MathSolver()
firebase_client = None  # Will be initialized lazily


@router.post("/upload", response_model=dict)
async def upload_file(file: UploadFile = File(...)):
    """Upload image or PDF file for processing"""
    try:
        # Process the uploaded file
        processed_content = await image_processor.process_file(file)
        return {"message": "File uploaded successfully", "content": processed_content}
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}") from e


@router.post("/solve", response_model=ProblemResponse)
async def solve_problem(problem: ProblemRequest):
    """Process and solve math problem"""
    try:
        # Extract text from image data and solve the math problem
        # For now, we'll assume the problem.image_data contains the text
        # In a real implementation, you'd decode the base64 image and extract text
        problem_text = "extracted text from image"  # This should be extracted from problem.image_data
        solution = await math_solver.solve(problem_text)
        
        # Convert MathSolution to ProblemResponse
        return ProblemResponse(
            original_text=problem_text,
            solution=solution.solution,
            steps=solution.steps,
            explanation=solution.explanation
        )
    except Exception as e:
        logger.error(f"Solving failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Solving failed: {str(e)}") from e


def get_firebase_client():
    """Get Firebase client instance (lazy initialization)"""
    global firebase_client
    if firebase_client is None:
        firebase_client = FirebaseClient()
    return firebase_client


@router.get("/history")
async def get_history(user_id: str):
    """Fetch user's solution history"""
    try:
        client = get_firebase_client()
        history = await client.get_user_history(user_id)
        return {"history": history}
    except Exception as e:
        logger.error(f"History retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"History retrieval failed: {str(e)}"
        ) from e


@router.delete("/history/{problem_id}")
async def delete_problem(problem_id: str, user_id: str):
    """Delete a specific problem from history"""
    try:
        client = get_firebase_client()
        await client.delete_problem(user_id, problem_id)
        return {"message": "Problem deleted successfully"}
    except Exception as e:
        logger.error(f"Deletion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}") from e
