import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..database.firebase_client import FirebaseClient
from ..models.problem import MathProblem, SolutionResponse
from ..services.image_processor import ImageProcessor
from ..services.math_solver import MathSolver

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
image_processor = ImageProcessor()
math_solver = MathSolver()
firebase_client = FirebaseClient()


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


@router.post("/solve", response_model=SolutionResponse)
async def solve_problem(problem: MathProblem):
    """Process and solve math problem"""
    try:
        # Solve the math problem
        solution = await math_solver.solve(problem)
        return solution
    except Exception as e:
        logger.error(f"Solving failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Solving failed: {str(e)}") from e


@router.get("/history")
async def get_history(user_id: str):
    """Fetch user's solution history"""
    try:
        history = await firebase_client.get_user_history(user_id)
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
        await firebase_client.delete_problem(user_id, problem_id)
        return {"message": "Problem deleted successfully"}
    except Exception as e:
        logger.error(f"Deletion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}") from e
