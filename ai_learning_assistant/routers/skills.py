"""Skills API Router - Team 1 endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from models.skills import SkillAnalysisRequest, SkillAnalysisResponse, SkillProfile
from agents.skill_profiler import SkillProfilerAgent
from services.llm_service import LLMService

router = APIRouter(prefix="/skills", tags=["Skills"])


def get_skill_profiler() -> SkillProfilerAgent:
    return SkillProfilerAgent(LLMService())


@router.post("/analyze", response_model=SkillAnalysisResponse)
async def analyze_skills(
    request: SkillAnalysisRequest,
    agent: SkillProfilerAgent = Depends(get_skill_profiler),
):
    """
    POST /skills/analyze
    
    Analyze employee skills from resume, certifications, project history,
    and self-assessment. Returns extracted skills, role mapping, and gap analysis.
    """
    try:
        result = await agent.analyze_skills(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/employee/{employee_id}", response_model=SkillProfile)
async def get_employee_skills(
    employee_id: str,
    agent: SkillProfilerAgent = Depends(get_skill_profiler),
):
    """
    GET /employee/{id}/skills
    
    Retrieve the stored skill profile for an employee.
    """
    try:
        profile = await agent.get_employee_skills(employee_id)
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/roles")
async def get_available_roles():
    """Get all available target roles and their required skills."""
    return SkillProfilerAgent.ROLE_SKILL_REQUIREMENTS
