"""
AI Learning Assistant - Main Application

A personal AI career coach that continuously assesses skills, recommends learning,
generates assessments, and tracks progress.

Architecture:
- Team 1: Employee Skill Profiler Agent
- Team 2: Learning Recommendation Agent
- Team 3: AI Tutor Agent
- Team 4: Quiz & Evaluation Agent
- Team 5: Progress Tracking Agent
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import skills, learning, assessments, dashboard

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-powered learning assistant for employee skill development",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Register routers
app.include_router(skills.router)
app.include_router(learning.router)
app.include_router(assessments.router)
app.include_router(dashboard.router)


@app.get("/")
async def root(request: Request):
    """Serve the main frontend portal."""
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
