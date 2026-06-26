"""
Team 5 - Progress Tracking Agent

Goal: Track learning progress, generate reports, and provide manager dashboards.
Aggregates data from all other agents to show comprehensive progress.
"""

from datetime import datetime
from models.learning import LearningProgress
from models.assessment import AssessmentResult
from models.skills import SkillGap


class ProgressTrackerAgent:
    """Agent that tracks and reports on employee learning progress."""

    def __init__(self):
        self._progress: dict[str, list[LearningProgress]] = {}
        self._milestones: dict[str, list[dict]] = {}

    def record_progress(self, progress: LearningProgress) -> None:
        """Record course progress for an employee."""
        if progress.employee_id not in self._progress:
            self._progress[progress.employee_id] = []
        
        # Update existing or add new
        existing = next(
            (p for p in self._progress[progress.employee_id] if p.course_id == progress.course_id),
            None,
        )
        if existing:
            existing.progress_percent = progress.progress_percent
            existing.completed = progress.completed
            existing.score = progress.score
        else:
            self._progress[progress.employee_id].append(progress)

    def get_employee_progress(self, employee_id: str) -> dict:
        """Get comprehensive progress report for an employee."""
        
        progress_list = self._progress.get(employee_id, [])
        
        total_courses = len(progress_list)
        completed = sum(1 for p in progress_list if p.completed)
        in_progress = sum(1 for p in progress_list if not p.completed and p.progress_percent > 0)
        avg_progress = (
            sum(p.progress_percent for p in progress_list) / total_courses
            if total_courses > 0
            else 0
        )
        
        return {
            "employee_id": employee_id,
            "total_courses": total_courses,
            "completed_courses": completed,
            "in_progress_courses": in_progress,
            "not_started_courses": total_courses - completed - in_progress,
            "average_progress": round(avg_progress, 1),
            "completion_rate": round((completed / total_courses) * 100, 1) if total_courses > 0 else 0,
        }

    def get_manager_dashboard(self, manager_id: str, team_member_ids: list[str]) -> dict:
        """Generate manager dashboard with team-wide progress overview."""
        
        team_progress = []
        for emp_id in team_member_ids:
            team_progress.append(self.get_employee_progress(emp_id))
        
        total_team_courses = sum(p["total_courses"] for p in team_progress)
        total_completed = sum(p["completed_courses"] for p in team_progress)
        
        return {
            "manager_id": manager_id,
            "team_size": len(team_member_ids),
            "team_members": team_progress,
            "team_total_courses": total_team_courses,
            "team_completed_courses": total_completed,
            "team_completion_rate": (
                round((total_completed / total_team_courses) * 100, 1)
                if total_team_courses > 0
                else 0
            ),
            "top_performers": self._get_top_performers(team_progress),
            "needs_attention": self._get_needs_attention(team_progress),
        }

    def get_skill_progress(
        self, employee_id: str, original_gaps: list[SkillGap], results: list[AssessmentResult]
    ) -> list[dict]:
        """Calculate skill improvement based on assessments taken."""
        
        skill_updates = []
        for gap in original_gaps:
            relevant_results = [r for r in results if r.passed]
            improvement = len(relevant_results) * 1  # Simplified improvement calc
            
            new_level = min(10, gap.current_level + improvement)
            remaining_gap = max(0, gap.required_level - new_level)
            
            skill_updates.append({
                "skill": gap.skill_name,
                "original_level": gap.current_level,
                "current_level": new_level,
                "target_level": gap.required_level,
                "remaining_gap": remaining_gap,
                "status": "achieved" if remaining_gap == 0 else "in_progress",
            })
        
        return skill_updates

    def _get_top_performers(self, team_progress: list[dict]) -> list[dict]:
        """Identify top performers in the team."""
        sorted_team = sorted(team_progress, key=lambda x: x["completion_rate"], reverse=True)
        return sorted_team[:3]

    def _get_needs_attention(self, team_progress: list[dict]) -> list[dict]:
        """Identify team members who may need support."""
        return [p for p in team_progress if p["average_progress"] < 25 and p["total_courses"] > 0]
