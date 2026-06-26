from pydantic import BaseModel, Field
from typing import Optional


class Skill(BaseModel):
    name: str
    level: int = Field(ge=1, le=10, description="Skill level from 1 to 10")
    category: str = ""
    source: str = ""  # resume, self-assessment, certification, etc.


class SkillProfile(BaseModel):
    employee_id: str
    skills: list[Skill] = []
    current_role: str = ""
    target_role: str = ""


class SkillGap(BaseModel):
    skill_name: str
    current_level: int
    required_level: int
    gap: int
    priority: str  # high, medium, low


class SkillAnalysisRequest(BaseModel):
    employee_id: str
    resume_text: Optional[str] = None
    certifications: list[str] = []
    project_history: list[str] = []
    self_assessment: Optional[dict] = None


class SkillAnalysisResponse(BaseModel):
    employee_id: str
    extracted_skills: dict[str, int]  # skill_name: level
    current_role: str
    target_role: str
    skill_gaps: list[SkillGap]
    recommendations: list[str]
