import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..database.firebase_client import FirebaseClient
from ..models.problem import ProblemResponse
from ..services.math_solver import MathSolver

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
math_solver = MathSolver()
firebase_client = None  # Will be initialized lazily

@router.post("/solve", response_model=ProblemResponse)
async def solve_problem(file: UploadFile = File(...)):
    """Process and solve math problem"""
    try:
        solution = await math_solver.solve(file)
        
        return solution
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
