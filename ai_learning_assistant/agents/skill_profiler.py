"""
Team 1 - Employee Skill Profiler Agent

Goal: Understand employee capabilities by extracting skills from multiple sources,
mapping to roles, and performing gap analysis.

Inputs: Resume, LinkedIn profile, Certifications, Project history, Self-assessment
Outputs: Skill profile, Role mapping, Gap analysis
"""

from models.skills import (
    Skill,
    SkillProfile,
    SkillGap,
    SkillAnalysisRequest,
    SkillAnalysisResponse,
)
from services.llm_service import LLMService


class SkillProfilerAgent:
    """Agent that profiles employee skills using LLM-based extraction and classification."""

    ROLE_SKILL_REQUIREMENTS = {
        "AI Solution Architect": {
            "Python": 8, "Machine Learning": 8, "Deep Learning": 7,
            "NLP": 7, "Cloud Architecture": 8, "AI": 9,
            "System Design": 8, "MLOps": 7, "Data Engineering": 6,
        },
        "Senior Java Developer": {
            "Java": 9, "Spring Boot": 8, "Microservices": 8,
            "SQL": 7, "Docker": 7, "Kubernetes": 6, "CI/CD": 7,
        },
        "Full Stack Developer": {
            "JavaScript": 8, "React": 8, "Node.js": 8,
            "SQL": 7, "REST APIs": 8, "Docker": 6, "Git": 7,
        },
        "Data Engineer": {
            "Python": 8, "SQL": 9, "Spark": 8, "Kafka": 7,
            "Airflow": 7, "Cloud": 7, "Data Modeling": 8,
        },
        "Cloud Architect": {
            "AWS": 9, "Azure": 7, "Terraform": 8,
            "Kubernetes": 8, "Networking": 8, "Security": 7,
            "System Design": 9,
        },
        "ML Engineer": {
            "Python": 9, "Machine Learning": 9, "Deep Learning": 8,
            "MLOps": 8, "Docker": 7, "Data Engineering": 7,
            "Mathematics": 8,
        },
    }

    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    async def analyze_skills(self, request: SkillAnalysisRequest) -> SkillAnalysisResponse:
        """Main entry point - analyze employee skills from all available sources."""
        
        # Step 1: Extract skills from provided inputs
        extracted_skills = await self._extract_skills(request)
        
        # Step 2: Determine current and target roles
        current_role, target_role = await self._map_roles(extracted_skills, request)
        
        # Step 3: Perform gap analysis
        skill_gaps = self._analyze_gaps(extracted_skills, target_role)
        
        # Step 4: Generate recommendations
        recommendations = self._generate_recommendations(skill_gaps)
        
        return SkillAnalysisResponse(
            employee_id=request.employee_id,
            extracted_skills=extracted_skills,
            current_role=current_role,
            target_role=target_role,
            skill_gaps=skill_gaps,
            recommendations=recommendations,
        )

    async def _extract_skills(self, request: SkillAnalysisRequest) -> dict[str, int]:
        """Extract skills and proficiency levels from all available sources."""
        
        sources_text = []
        
        if request.resume_text:
            sources_text.append(f"Resume:\n{request.resume_text}")
        
        if request.certifications:
            sources_text.append(f"Certifications: {', '.join(request.certifications)}")
        
        if request.project_history:
            sources_text.append(f"Projects: {', '.join(request.project_history)}")
        
        if request.self_assessment:
            sources_text.append(f"Self-Assessment: {request.self_assessment}")

        if not sources_text:
            return {}

        prompt = f"""Analyze the following employee information and extract technical skills 
with proficiency levels (1-10 scale).

{chr(10).join(sources_text)}

Return a JSON object mapping skill names to proficiency levels.
Example: {{"Python": 8, "React": 7, "AWS": 5, "AI": 2}}

Only return the JSON object, nothing else."""

        response = await self.llm.generate(prompt)
        
        try:
            import json
            skills = json.loads(response)
            return {k: max(1, min(10, int(v))) for k, v in skills.items()}
        except (json.JSONDecodeError, ValueError):
            return self._fallback_extraction(request)

    def _fallback_extraction(self, request: SkillAnalysisRequest) -> dict[str, int]:
        """Fallback skill extraction when LLM parsing fails."""
        skills = {}
        if request.self_assessment:
            for skill, level in request.self_assessment.items():
                if isinstance(level, (int, float)):
                    skills[skill] = max(1, min(10, int(level)))
        return skills

    async def _map_roles(
        self, skills: dict[str, int], request: SkillAnalysisRequest
    ) -> tuple[str, str]:
        """Identify current role and target role based on skill profile."""
        
        prompt = f"""Given these skills and levels: {skills}

Available roles: {list(self.ROLE_SKILL_REQUIREMENTS.keys())}

1. What is the most likely CURRENT role based on these skills?
2. What would be a good TARGET role for career growth?

Return exactly two lines:
Current: <role name>
Target: <role name>"""

        response = await self.llm.generate(prompt)
        
        current_role = "Unknown"
        target_role = "Unknown"
        
        for line in response.strip().split("\n"):
            if line.startswith("Current:"):
                current_role = line.replace("Current:", "").strip()
            elif line.startswith("Target:"):
                target_role = line.replace("Target:", "").strip()
        
        return current_role, target_role

    def _analyze_gaps(self, current_skills: dict[str, int], target_role: str) -> list[SkillGap]:
        """Compare current skills against target role requirements."""
        
        required_skills = self.ROLE_SKILL_REQUIREMENTS.get(target_role, {})
        gaps = []
        
        for skill_name, required_level in required_skills.items():
            current_level = current_skills.get(skill_name, 0)
            gap = required_level - current_level
            
            if gap > 0:
                priority = "high" if gap >= 5 else "medium" if gap >= 3 else "low"
                gaps.append(SkillGap(
                    skill_name=skill_name,
                    current_level=current_level,
                    required_level=required_level,
                    gap=gap,
                    priority=priority,
                ))
        
        # Sort by gap size descending
        gaps.sort(key=lambda g: g.gap, reverse=True)
        return gaps

    def _generate_recommendations(self, gaps: list[SkillGap]) -> list[str]:
        """Generate learning recommendations based on skill gaps."""
        
        recommendations = []
        
        high_priority = [g for g in gaps if g.priority == "high"]
        medium_priority = [g for g in gaps if g.priority == "medium"]
        
        if high_priority:
            skills_list = ", ".join(g.skill_name for g in high_priority[:3])
            recommendations.append(
                f"Priority Focus: Start with {skills_list} - these have the largest gaps"
            )
        
        if medium_priority:
            skills_list = ", ".join(g.skill_name for g in medium_priority[:3])
            recommendations.append(
                f"Secondary Focus: Build on {skills_list} to strengthen your profile"
            )
        
        if not gaps:
            recommendations.append(
                "You're well-aligned with your target role! Consider advanced specialization."
            )
        
        return recommendations

    async def get_employee_skills(self, employee_id: str) -> SkillProfile:
        """Retrieve stored skill profile for an employee."""
        # In production, this would query a database
        # For now, return a placeholder
        return SkillProfile(employee_id=employee_id)
