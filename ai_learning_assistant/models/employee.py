from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class Role(str, Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    ADMIN = "admin"


class Employee(BaseModel):
    id: str
    name: str
    email: str
    role: Role = Role.EMPLOYEE
    current_position: str
    department: str
    target_role: Optional[str] = None
    manager_id: Optional[str] = None


class EmployeeCreate(BaseModel):
    name: str
    email: str
    role: Role = Role.EMPLOYEE
    current_position: str
    department: str
    target_role: Optional[str] = None
    manager_id: Optional[str] = None


class EmployeeProfile(BaseModel):
    employee: Employee
    resume_text: Optional[str] = None
    linkedin_url: Optional[str] = None
    certifications: list[str] = []
    project_history: list[str] = []
    self_assessment: Optional[dict] = None
