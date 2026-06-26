"""
Team 4 - Quiz & Evaluation Agent

Goal: Generate assessments, administer quizzes, and evaluate employee knowledge.
Uses LLM to create contextual questions and grade responses.
"""

import json
import uuid
from models.assessment import Question, Assessment, AssessmentResult
from services.llm_service import LLMService


class AssessmentAgent:
    """Agent that generates and evaluates skill assessments."""

    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        self._assessments: dict[str, Assessment] = {}
        self._results: dict[str, list[AssessmentResult]] = {}

    async def generate_assessment(
        self, skill: str, difficulty: str = "medium", num_questions: int = 5
    ) -> Assessment:
        """Generate a skill assessment with AI-created questions."""
        
        prompt = f"""Generate {num_questions} multiple-choice questions to assess knowledge of {skill} 
at {difficulty} difficulty level.

Return a JSON array where each question has:
- "text": the question text
- "options": array of 4 answer choices
- "correct_answer": index (0-3) of the correct option
- "explanation": why the correct answer is right

Only return the JSON array, nothing else."""

        response = await self.llm.generate(prompt)
        
        try:
            questions_data = json.loads(response)
        except json.JSONDecodeError:
            questions_data = self._generate_fallback_questions(skill, num_questions)
        
        questions = []
        for i, q_data in enumerate(questions_data):
            questions.append(Question(
                id=f"q_{uuid.uuid4().hex[:8]}",
                text=q_data["text"],
                options=q_data["options"],
                correct_answer=q_data["correct_answer"],
                explanation=q_data.get("explanation", ""),
                skill=skill,
                difficulty=difficulty,
            ))
        
        assessment = Assessment(
            id=f"assess_{uuid.uuid4().hex[:8]}",
            title=f"{skill} Assessment - {difficulty.title()}",
            skill=skill,
            questions=questions,
        )
        
        self._assessments[assessment.id] = assessment
        return assessment

    def evaluate_assessment(
        self, employee_id: str, assessment_id: str, answers: list[int], time_taken: float
    ) -> AssessmentResult:
        """Evaluate submitted assessment answers."""
        
        assessment = self._assessments.get(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")
        
        correct_count = 0
        for i, (answer, question) in enumerate(zip(answers, assessment.questions)):
            if answer == question.correct_answer:
                correct_count += 1
        
        score = (correct_count / len(assessment.questions)) * 100 if assessment.questions else 0
        
        result = AssessmentResult(
            employee_id=employee_id,
            assessment_id=assessment_id,
            score=score,
            passed=score >= assessment.passing_score,
            answers=answers,
            time_taken_minutes=time_taken,
        )
        
        if employee_id not in self._results:
            self._results[employee_id] = []
        self._results[employee_id].append(result)
        
        return result

    def get_results(self, employee_id: str) -> list[AssessmentResult]:
        """Get all assessment results for an employee."""
        return self._results.get(employee_id, [])

    def get_assessment(self, assessment_id: str) -> Assessment | None:
        """Retrieve an assessment by ID."""
        return self._assessments.get(assessment_id)

    def _generate_fallback_questions(self, skill: str, num_questions: int) -> list[dict]:
        """Generate basic fallback questions when LLM parsing fails."""
        return [
            {
                "text": f"What is a core concept of {skill}?",
                "options": [
                    f"Fundamental principle of {skill}",
                    "Unrelated concept",
                    "Incorrect option",
                    "Another incorrect option",
                ],
                "correct_answer": 0,
                "explanation": f"This tests basic understanding of {skill}.",
            }
            for _ in range(num_questions)
        ]
