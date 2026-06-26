"""
Team 3 - AI Tutor Agent

Goal: Provide interactive AI tutoring for employees as they learn new skills.
Acts as a conversational learning companion.
"""

from models.assessment import TutorMessage, TutorSession
from services.llm_service import LLMService


class AITutorAgent:
    """Agent that provides interactive AI tutoring during learning."""

    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        self._sessions: dict[str, TutorSession] = {}

    async def start_session(self, employee_id: str, topic: str) -> TutorSession:
        """Start a new tutoring session for a given topic."""
        
        session = TutorSession(employee_id=employee_id, topic=topic)
        
        # Generate initial greeting/context
        intro_prompt = f"""You are an AI tutor helping an employee learn about {topic}.
Start by giving a brief overview of the topic and ask what specific aspect they'd like to focus on.
Keep it concise and encouraging."""

        intro_response = await self.llm.generate(intro_prompt)
        
        session.messages.append(TutorMessage(role="assistant", content=intro_response))
        
        session_key = f"{employee_id}_{topic}"
        self._sessions[session_key] = session
        
        return session

    async def chat(self, employee_id: str, topic: str, user_message: str) -> str:
        """Process a user message and return tutor response."""
        
        session_key = f"{employee_id}_{topic}"
        session = self._sessions.get(session_key)
        
        if not session:
            session = await self.start_session(employee_id, topic)
        
        # Add user message
        session.messages.append(TutorMessage(role="user", content=user_message))
        
        # Build conversation context
        system_prompt = f"""You are an expert AI tutor specializing in {topic}.
Your role is to:
- Explain concepts clearly with examples
- Ask follow-up questions to check understanding
- Provide practice exercises when appropriate
- Encourage the learner and track their progress
- Break complex topics into digestible parts

Keep responses focused and educational. Use analogies when helpful."""

        messages_context = "\n".join(
            f"{m.role}: {m.content}" for m in session.messages[-10:]  # Last 10 messages
        )
        
        prompt = f"{system_prompt}\n\nConversation so far:\n{messages_context}\n\nassistant:"
        
        response = await self.llm.generate(prompt)
        
        session.messages.append(TutorMessage(role="assistant", content=response))
        self._sessions[session_key] = session
        
        return response

    async def explain_concept(self, topic: str, concept: str, level: str = "intermediate") -> str:
        """Get a detailed explanation of a specific concept."""
        
        prompt = f"""Explain the concept of "{concept}" in the context of {topic}.
Target audience: {level} level learner.
Include:
1. A clear definition
2. A real-world analogy
3. A simple code example if applicable
4. Key points to remember"""

        return await self.llm.generate(prompt)

    def get_session(self, employee_id: str, topic: str) -> TutorSession | None:
        """Retrieve an existing tutor session."""
        session_key = f"{employee_id}_{topic}"
        return self._sessions.get(session_key)
