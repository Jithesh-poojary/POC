"""Assessment API Router - Team 3 & 4 endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from agents.ai_tutor import AITutorAgent
from agents.assessment import AssessmentAgent
from services.llm_service import LLMService

router = APIRouter(prefix="/assessments", tags=["Assessments"])

# Shared instances
_tutor_agent = AITutorAgent(LLMService())
_assessment_agent = AssessmentAgent(LLMService())


class GenerateAssessmentRequest(BaseModel):
    skill: str
    difficulty: str = "medium"
    num_questions: int = 5


class SubmitAnswersRequest(BaseModel):
    employee_id: str
    assessment_id: str
    answers: list[int]
    time_taken_minutes: float


class TutorChatRequest(BaseModel):
    employee_id: str
    topic: str
    message: str


@router.post("/generate")
async def generate_assessment(request: GenerateAssessmentRequest):
    """Generate a new skill assessment with AI-created questions."""
    try:
        assessment = await _assessment_agent.generate_assessment(
            skill=request.skill,
            difficulty=request.difficulty,
            num_questions=request.num_questions,
        )
        return assessment
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit")
async def submit_assessment(request: SubmitAnswersRequest):
    """Submit assessment answers and get evaluation results."""
    try:
        result = _assessment_agent.evaluate_assessment(
            employee_id=request.employee_id,
            assessment_id=request.assessment_id,
            answers=request.answers,
            time_taken=request.time_taken_minutes,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{employee_id}")
async def get_results(employee_id: str):
    """Get all assessment results for an employee."""
    return _assessment_agent.get_results(employee_id)


@router.get("/{assessment_id}")
async def get_assessment(assessment_id: str):
    """Get assessment details by ID."""
    assessment = _assessment_agent.get_assessment(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


# AI Tutor Endpoints
@router.post("/tutor/chat")
async def tutor_chat(request: TutorChatRequest):
    """Chat with the AI tutor on a specific topic."""
    try:
        response = await _tutor_agent.chat(
            employee_id=request.employee_id,
            topic=request.topic,
            user_message=request.message,
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tutor/explain")
async def explain_concept(topic: str, concept: str, level: str = "intermediate"):
    """Get a detailed explanation of a concept."""
    try:
        explanation = await _tutor_agent.explain_concept(topic, concept, level)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
