import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ..core.auth import get_current_user
from ..database.firebase_client import FirebaseClient
from ..models.problem import ProblemResponse
from ..services.math_solver import MathSolver

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
math_solver = MathSolver()
firebase_client = None  # Will be initialized lazily

@router.post("/solve", response_model=ProblemResponse)
async def solve_problem(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Process and solve math problem (requires authentication)"""
    try:
        user_id = current_user["uid"]
        logger.info(f"Processing math problem for user: {user_id}")
        
        solution = await math_solver.solve(file)
        
        # Optionally save the solution to user's history
        try:
            client = get_firebase_client()
            problem_data = {
                "question": solution.question,
                "answer": solution.answer.dict(),
                "user_id": user_id,
                "file_name": file.filename,
                "content_type": file.content_type,
            }
            await client.save_solution(user_id, problem_data)
            logger.info(f"Solution saved to history for user: {user_id}")
        except Exception as save_error:
            logger.warning(f"Failed to save solution to history: {str(save_error)}")
            # Don't fail the request if history saving fails
        
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
async def get_history(current_user: dict = Depends(get_current_user)):
    """Fetch user's solution history (requires authentication)"""
    try:
        user_id = current_user["uid"]
        logger.info(f"Fetching history for user: {user_id}")
        
        client = get_firebase_client()
        history = await client.get_user_history(user_id)
        
        return {
            "history": history,
            "user_id": user_id,
            "total_problems": len(history)
        }
    except Exception as e:
        logger.error(f"History retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"History retrieval failed: {str(e)}"
        ) from e


@router.delete("/history/{problem_id}")
async def delete_problem(
    problem_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """Delete a specific problem from history (requires authentication)"""
    try:
        user_id = current_user["uid"]
        logger.info(f"Deleting problem {problem_id} for user: {user_id}")
        
        client = get_firebase_client()
        await client.delete_problem(user_id, problem_id)
        
        return {
            "message": "Problem deleted successfully",
            "problem_id": problem_id,
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Deletion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}") from e
