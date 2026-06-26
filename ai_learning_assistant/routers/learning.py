"""Learning API Router - Team 2 endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from models.skills import SkillGap
from models.learning import LearningPath, LearningProgress
from agents.learning_recommender import LearningRecommenderAgent
from agents.progress_tracker import ProgressTrackerAgent
from services.llm_service import LLMService
from services.vector_db import VectorDBService
from pydantic import BaseModel

router = APIRouter(prefix="/learning", tags=["Learning"])

# Shared instances
_vector_db = VectorDBService()
_progress_tracker = ProgressTrackerAgent()


def get_recommender() -> LearningRecommenderAgent:
    return LearningRecommenderAgent(LLMService(), _vector_db)


class LearningPathRequest(BaseModel):
    employee_id: str
    target_role: str
    skill_gaps: list[SkillGap]


@router.post("/recommend", response_model=LearningPath)
async def recommend_learning_path(
    request: LearningPathRequest,
    agent: LearningRecommenderAgent = Depends(get_recommender),
):
    """Generate personalized learning path based on skill gaps."""
    try:
        path = await agent.recommend_learning_path(
            request.employee_id, request.target_role, request.skill_gaps
        )
        return path
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/progress")
async def update_progress(progress: LearningProgress):
    """Update learning progress for a course."""
    _progress_tracker.record_progress(progress)
    return {"status": "updated", "progress": progress}


@router.get("/progress/{employee_id}")
async def get_progress(employee_id: str):
    """Get learning progress for an employee."""
    return _progress_tracker.get_employee_progress(employee_id)
