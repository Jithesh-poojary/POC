from pydantic import BaseModel
from typing import Optional


class Question(BaseModel):
    id: str
    text: str
    options: list[str]
    correct_answer: int  # index of correct option
    explanation: str
    skill: str
    difficulty: str  # easy, medium, hard


class Assessment(BaseModel):
    id: str
    title: str
    skill: str
    questions: list[Question]
    passing_score: float = 70.0


class AssessmentResult(BaseModel):
    employee_id: str
    assessment_id: str
    score: float
    passed: bool
    answers: list[int]
    time_taken_minutes: float


class TutorMessage(BaseModel):
    role: str  # user, assistant
    content: str


class TutorSession(BaseModel):
    employee_id: str
    topic: str
    messages: list[TutorMessage] = []
