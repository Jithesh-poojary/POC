"""Dashboard API Router - Team 5 endpoints (Manager Dashboard)."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agents.progress_tracker import ProgressTrackerAgent

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

_progress_tracker = ProgressTrackerAgent()


class ManagerDashboardRequest(BaseModel):
    manager_id: str
    team_member_ids: list[str]


@router.post("/manager")
async def get_manager_dashboard(request: ManagerDashboardRequest):
    """Get manager dashboard with team-wide learning progress."""
    try:
        dashboard = _progress_tracker.get_manager_dashboard(
            manager_id=request.manager_id,
            team_member_ids=request.team_member_ids,
        )
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/employee/{employee_id}")
async def get_employee_dashboard(employee_id: str):
    """Get individual employee progress dashboard."""
    return _progress_tracker.get_employee_progress(employee_id)
