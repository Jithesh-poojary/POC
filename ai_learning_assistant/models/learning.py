from pydantic import BaseModel
from typing import Optional
from enum import Enum


class CourseLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Course(BaseModel):
    id: str
    title: str
    description: str
    skills_covered: list[str]
    level: CourseLevel
    duration_hours: float
    provider: str
    url: Optional[str] = None


class LearningPath(BaseModel):
    employee_id: str
    target_role: str
    courses: list[Course]
    estimated_duration_hours: float
    priority_skills: list[str]


class LearningProgress(BaseModel):
    employee_id: str
    course_id: str
    progress_percent: float = 0.0
    completed: bool = False
    score: Optional[float] = None
