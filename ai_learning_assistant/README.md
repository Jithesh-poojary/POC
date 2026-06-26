# AI Learning Assistant for Employees

A personal AI career coach that continuously assesses skills, recommends learning, generates assessments, and tracks progress.

## Architecture

```
Frontend Portal
      |
API Gateway (FastAPI)
      |
---------------------------------
|       |       |       |       |
Team1   Team2   Team3   Team4   Team5
Agent   Agent   Agent   Agent   Agent
---------------------------------
      |
LLM + Vector DB + Course Catalog
```

### Agents

| Team | Agent | Responsibility |
|------|-------|----------------|
| 1 | Skill Profiler | Extract skills, map roles, gap analysis |
| 2 | Learning Recommender | Personalized course recommendations |
| 3 | AI Tutor | Interactive learning assistance |
| 4 | Assessment | Generate quizzes, evaluate knowledge |
| 5 | Progress Tracker | Track progress, manager dashboards |

## Setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your OpenAI API key

# Run the application
python main.py
```

The app will be available at http://localhost:8000

## API Endpoints

### Team 1 - Skills
- `POST /skills/analyze` - Analyze employee skills
- `GET /skills/employee/{id}` - Get employee skill profile
- `GET /skills/roles` - List available target roles

### Team 2 - Learning
- `POST /learning/recommend` - Generate learning path
- `POST /learning/progress` - Update course progress
- `GET /learning/progress/{employee_id}` - Get progress

### Team 3 & 4 - Assessments & Tutor
- `POST /assessments/generate` - Generate skill quiz
- `POST /assessments/submit` - Submit quiz answers
- `GET /assessments/results/{employee_id}` - Get results
- `POST /assessments/tutor/chat` - Chat with AI tutor
- `POST /assessments/tutor/explain` - Get concept explanation

### Team 5 - Dashboard
- `POST /dashboard/manager` - Manager team dashboard
- `GET /dashboard/employee/{employee_id}` - Employee dashboard

## Workflow

1. **Employee Login** → Access portal
2. **Skill Assessment** → Submit resume/certs/self-assessment
3. **Skill Gap Analysis** → AI identifies gaps vs target role
4. **Learning Recommendation** → Personalized course path
5. **Course Consumption** → Track progress
6. **AI Tutor Assistance** → Ask questions while learning
7. **Quiz & Evaluation** → Test knowledge
8. **Progress Tracking** → Monitor improvement
9. **Manager Dashboard** → Team-wide visibility
