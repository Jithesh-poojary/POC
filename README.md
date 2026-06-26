# AI Learning Assistant

This repository contains an AI-powered learning assistant application built with FastAPI.

## Getting Started

1. Open PowerShell or Command Prompt.
2. Change into the project folder:

```powershell
cd C:\POC\ai_learning_assistant
```

3. Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\activate
```

4. Install dependencies:

```powershell
pip install -r requirements.txt
```

5. Copy the example environment file and update any required variables:

```powershell
copy .env.example .env
```

6. Start the application:

```powershell
python main.py
```

## Access the App

Open your browser to:

```text
http://localhost:8000
```

## Notes

- The app uses FastAPI and Uvicorn.
- The frontend is served from `static/` and `templates/`.
- If you make code changes, the server will reload automatically because Uvicorn is started with `reload=True`.

## Useful Commands

```powershell
# Activate the virtual environment
venv\Scripts\activate

# Install or update dependencies
pip install -r requirements.txt

# Run the app
python main.py
```
