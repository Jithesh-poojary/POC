"""LLM Service - Handles all interactions with the language model."""

import json
from config import settings


class LLMService:
    """Service for interacting with OpenAI-compatible LLMs."""

    def __init__(self):
        self._client = None
        self.model = settings.LLM_MODEL

    @property
    def client(self):
        if self._client is None:
            api_key = settings.OPENAI_API_KEY
            if not api_key:
                return None
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=api_key)
        return self._client

    async def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Generate a response from the LLM."""
        
        if not self.client:
            return self._mock_response(prompt)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"LLM Error: {str(e)}"

    async def generate_with_system(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.7
    ) -> str:
        """Generate a response with a system prompt."""
        
        if not self.client:
            return self._mock_response(user_prompt)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"LLM Error: {str(e)}"

    async def generate_json(self, prompt: str) -> str:
        """Generate a JSON response from the LLM."""
        
        if not self.client:
            return self._mock_response(prompt)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content or "{}"
        except Exception as e:
            return "{}"

    def _mock_response(self, prompt: str) -> str:
        """Provide demo responses when no API key is configured."""
        prompt_lower = prompt.lower()

        # Skill extraction
        if "extract" in prompt_lower and "skill" in prompt_lower:
            return json.dumps({
                "Python": 7, "Java": 8, "JavaScript": 6,
                "SQL": 7, "Docker": 5, "AWS": 4, "React": 5,
                "Machine Learning": 3, "Git": 8, "REST APIs": 7
            })

        # Role mapping
        if "current role" in prompt_lower or "target role" in prompt_lower:
            return "Current: Senior Java Developer\nTarget: AI Solution Architect"

        # Quiz generation
        if "multiple-choice" in prompt_lower or "questions" in prompt_lower:
            skill = "the topic"
            for word in ["python", "java", "aws", "react", "machine learning", "sql", "docker", "system design"]:
                if word in prompt_lower:
                    skill = word.title()
                    break
            return json.dumps([
                {
                    "text": f"What is a key feature of {skill}?",
                    "options": [
                        f"{skill} supports multiple paradigms",
                        f"{skill} only works on Windows",
                        f"{skill} cannot handle large datasets",
                        f"{skill} requires a license fee"
                    ],
                    "correct_answer": 0,
                    "explanation": f"{skill} is known for supporting multiple paradigms and being versatile."
                },
                {
                    "text": f"Which of the following best describes {skill}?",
                    "options": [
                        "A hardware component",
                        f"A technology/tool used in software development",
                        "A type of database only",
                        "An operating system"
                    ],
                    "correct_answer": 1,
                    "explanation": f"{skill} is a technology/tool widely used in modern software development."
                },
                {
                    "text": f"What is a common use case for {skill}?",
                    "options": [
                        "Cooking recipes",
                        "Building software applications",
                        "Mechanical engineering only",
                        "Graphic design exclusively"
                    ],
                    "correct_answer": 1,
                    "explanation": f"{skill} is commonly used for building software applications."
                },
                {
                    "text": f"Which community aspect is true about {skill}?",
                    "options": [
                        "It has no community support",
                        "It has a large active community and ecosystem",
                        "Only 10 people use it worldwide",
                        "It was discontinued in 2020"
                    ],
                    "correct_answer": 1,
                    "explanation": f"{skill} has a thriving community with extensive libraries and resources."
                },
                {
                    "text": f"What skill level requires understanding {skill} fundamentals?",
                    "options": [
                        "No level - it's not important",
                        "Only PhD researchers need it",
                        "Beginner to intermediate developers benefit from it",
                        "Only CTOs need to know this"
                    ],
                    "correct_answer": 2,
                    "explanation": f"Understanding {skill} fundamentals benefits developers at beginner to intermediate levels."
                }
            ])

        # Course suggestion
        if "suggest" in prompt_lower and "course" in prompt_lower:
            return json.dumps({
                "title": "Comprehensive Learning Course",
                "description": "A thorough course covering fundamentals to advanced topics",
                "duration_hours": 20.0,
                "provider": "Internal Academy"
            })

        # AI Tutor responses
        if "tutor" in prompt_lower or "explain" in prompt_lower or "learn" in prompt_lower:
            return (
                "Great question! Let me explain this concept clearly.\n\n"
                "This is a fundamental topic in software development. "
                "The key things to understand are:\n\n"
                "1. **Core Concept**: It provides a structured way to solve problems\n"
                "2. **Practical Use**: It's widely used in production systems\n"
                "3. **Best Practice**: Start with the basics and build up gradually\n\n"
                "Would you like me to dive deeper into any of these points, "
                "or shall I provide a code example?"
            )

        # Default conversational response
        return (
            "That's an interesting question! In the context of software development, "
            "this topic involves understanding core principles and applying them practically. "
            "I'd recommend starting with the fundamentals and progressively building your knowledge. "
            "Would you like me to elaborate on any specific aspect?"
        )
