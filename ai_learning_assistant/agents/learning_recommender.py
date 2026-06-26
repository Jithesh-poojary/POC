"""
Team 2 - Learning Recommendation Agent

Goal: Recommend personalized learning paths based on skill gaps and career goals.
Uses vector similarity to match courses to skill needs.
"""

from models.skills import SkillGap
from models.learning import Course, LearningPath, CourseLevel
from services.llm_service import LLMService
from services.vector_db import VectorDBService


class LearningRecommenderAgent:
    """Agent that recommends personalized learning paths based on skill gaps."""

    def __init__(self, llm_service: LLMService, vector_db: VectorDBService):
        self.llm = llm_service
        self.vector_db = vector_db

    async def recommend_learning_path(
        self, employee_id: str, target_role: str, skill_gaps: list[SkillGap]
    ) -> LearningPath:
        """Generate a personalized learning path based on skill gaps."""
        
        priority_skills = [g.skill_name for g in skill_gaps if g.priority in ("high", "medium")]
        
        # Find relevant courses using vector similarity
        courses = []
        for skill in priority_skills[:5]:  # Top 5 priority skills
            matching_courses = await self._find_courses_for_skill(skill, skill_gaps)
            courses.extend(matching_courses)
        
        # Remove duplicates and order by priority
        seen_ids = set()
        unique_courses = []
        for course in courses:
            if course.id not in seen_ids:
                seen_ids.add(course.id)
                unique_courses.append(course)
        
        total_hours = sum(c.duration_hours for c in unique_courses)
        
        return LearningPath(
            employee_id=employee_id,
            target_role=target_role,
            courses=unique_courses,
            estimated_duration_hours=total_hours,
            priority_skills=priority_skills,
        )

    async def _find_courses_for_skill(
        self, skill_name: str, gaps: list[SkillGap]
    ) -> list[Course]:
        """Find courses matching a specific skill need."""
        
        # Determine required level for the skill
        gap_info = next((g for g in gaps if g.skill_name == skill_name), None)
        if not gap_info:
            return []
        
        # Determine appropriate course level
        if gap_info.current_level <= 3:
            level = CourseLevel.BEGINNER
        elif gap_info.current_level <= 6:
            level = CourseLevel.INTERMEDIATE
        else:
            level = CourseLevel.ADVANCED
        
        # Search vector DB for relevant courses
        query = f"{skill_name} {level.value} course training"
        results = await self.vector_db.search_courses(query, top_k=3)
        
        if results:
            return results
        
        # Fallback: generate course suggestion
        return [await self._generate_course_suggestion(skill_name, level)]

    async def _generate_course_suggestion(
        self, skill_name: str, level: CourseLevel
    ) -> Course:
        """Use LLM to suggest a course when none found in catalog."""
        
        prompt = f"""Suggest a training course for learning {skill_name} at {level.value} level.
Return a JSON object with: title, description, duration_hours, provider.
Only return the JSON object."""

        response = await self.llm.generate(prompt)
        
        import json
        try:
            data = json.loads(response)
            return Course(
                id=f"gen_{skill_name.lower().replace(' ', '_')}_{level.value}",
                title=data.get("title", f"{skill_name} - {level.value.title()}"),
                description=data.get("description", f"Learn {skill_name}"),
                skills_covered=[skill_name],
                level=level,
                duration_hours=data.get("duration_hours", 10.0),
                provider=data.get("provider", "AI Generated"),
            )
        except (json.JSONDecodeError, ValueError):
            return Course(
                id=f"gen_{skill_name.lower().replace(' ', '_')}_{level.value}",
                title=f"{skill_name} - {level.value.title()} Course",
                description=f"Comprehensive {level.value} training in {skill_name}",
                skills_covered=[skill_name],
                level=level,
                duration_hours=10.0,
                provider="Recommended",
            )
