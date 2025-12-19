import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException

from models.student_tools import (
    StudentSession, StudentInteraction, StudentToolType,
    StudentToolResponse
)
from services.database import database
from services.openai_service import OpenAIService

class StudentService:
    def __init__(self):
        self.openai_service = OpenAIService()

    async def create_session(self, user_id: str) -> str:
        """Create a new student tools session"""
        collection = database.get_collection_by_name("student_sessions")
        session_id = str(uuid.uuid4())
        
        session = StudentSession(
            session_id=session_id,
            user_id=user_id,
        )
        await collection.insert_one(session.model_dump())
        return session_id

    async def _get_session(self, session_id: str) -> StudentSession:
        """Retrieve a session by ID or raise 404"""
        collection = database.get_collection_by_name("student_sessions")
        data = await collection.find_one({"session_id": session_id})
        if not data:
            raise HTTPException(status_code=404, detail="Session not found")
        return StudentSession(**data)

    async def _add_interaction(self, session_id: str, interaction: StudentInteraction):
        """Add interaction to session history"""
        collection = database.get_collection_by_name("student_sessions")
        await collection.update_one(
            {"session_id": session_id},
            {"$push": {"interactions": interaction.model_dump()}}
        )

    async def homework_helper(self, session_id: str, user_id: str, subject: str, question: str) -> StudentToolResponse:
        await self._get_session(session_id)
        
        system_prompt = f"You are an expert academic tutor for the subject of {subject}. Provide a clear, helpful, and educational answer to the student's question."
        
        ai_response = await self.openai_service.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
        )
        
        interaction = StudentInteraction(
            interaction_id=str(uuid.uuid4()),
            tool_type=StudentToolType.HOMEWORK,
            user_input=f"[{subject}] {question}",
            ai_response=ai_response,
            metadata={"subject": subject}
        )
        await self._add_interaction(session_id, interaction)
        return StudentToolResponse(
            interaction_id=interaction.interaction_id,
            ai_response=ai_response,
            timestamp=interaction.timestamp
        )

    async def essay_generator(self, session_id: str, user_id: str, topic: str, length: str, tone: str) -> StudentToolResponse:
        await self._get_session(session_id)
        
        system_prompt = f"You are a professional essay writer. Write a {length} essay on the topic of '{topic}' in a {tone} tone. Ensure proper structure with introduction, body paragraphs, and a conclusion."
        
        ai_response = await self.openai_service.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Write the essay about: {topic}"}
            ]
        )
        
        interaction = StudentInteraction(
            interaction_id=str(uuid.uuid4()),
            tool_type=StudentToolType.ESSAY,
            user_input=topic,
            ai_response=ai_response,
            metadata={"topic": topic, "length": length, "tone": tone}
        )
        await self._add_interaction(session_id, interaction)
        return StudentToolResponse(
            interaction_id=interaction.interaction_id,
            ai_response=ai_response,
            timestamp=interaction.timestamp
        )

    async def math_solver(self, session_id: str, user_id: str, problem: str) -> StudentToolResponse:
        await self._get_session(session_id)
        
        system_prompt = "You are a math tutor. Solve the following mathematical problem step-by-step. Explain the reasoning clearly for each step so the student can learn the process."
        
        ai_response = await self.openai_service.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": problem}
            ]
        )
        
        interaction = StudentInteraction(
            interaction_id=str(uuid.uuid4()),
            tool_type=StudentToolType.MATH,
            user_input=problem,
            ai_response=ai_response
        )
        await self._add_interaction(session_id, interaction)
        return StudentToolResponse(
            interaction_id=interaction.interaction_id,
            ai_response=ai_response,
            timestamp=interaction.timestamp
        )

    async def study_mode(self, session_id: str, user_id: str, topic: str, question: Optional[str] = None) -> StudentToolResponse:
        session = await self._get_session(session_id)
        
        system_prompt = f"You are a learning companion. The student wants to study '{topic}'. Facilitate an interactive learning session by explaining concepts and asking the student questions to check their understanding. Keep it engaging and encouraging."
        
        history = []
        for interact in session.interactions:
             if interact.tool_type == StudentToolType.STUDY:
                  history.append({"role": "user", "content": interact.user_input})
                  history.append({"role": "assistant", "content": interact.ai_response})
        
        current_input = question if question else f"I want to start studying {topic}"
        
        ai_response = await self.openai_service.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                *history[-4:], # Last 2 rounds of conversation
                {"role": "user", "content": current_input}
            ]
        )
        
        interaction = StudentInteraction(
            interaction_id=str(uuid.uuid4()),
            tool_type=StudentToolType.STUDY,
            user_input=current_input,
            ai_response=ai_response,
            metadata={"topic": topic}
        )
        await self._add_interaction(session_id, interaction)
        return StudentToolResponse(
            interaction_id=interaction.interaction_id,
            ai_response=ai_response,
            timestamp=interaction.timestamp
        )

    async def generate_flashcards(self, session_id: str, user_id: str, content: str, format: str) -> StudentToolResponse:
        await self._get_session(session_id)
        
        system_prompt = "You are an educational assistant. Create a set of flashcards from the provided content. Format each card as 'Front: [Question]' and 'Back: [Answer]'. Provide at least 5 cards if possible."
        
        ai_response = await self.openai_service.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ]
        )
        
        interaction = StudentInteraction(
            interaction_id=str(uuid.uuid4()),
            tool_type=StudentToolType.FLASHCARDS,
            user_input=content[:100] + "...",
            ai_response=ai_response
        )
        await self._add_interaction(session_id, interaction)
        return StudentToolResponse(
            interaction_id=interaction.interaction_id,
            ai_response=ai_response,
            timestamp=interaction.timestamp
        )

    async def summarize_text(self, session_id: str, user_id: str, content: str, detail_level: str) -> StudentToolResponse:
        await self._get_session(session_id)
        
        system_prompt = f"Summarize the following text. The detail level should be {detail_level}. Focus on key concepts and main takeaway points."
        
        ai_response = await self.openai_service.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ]
        )
        
        interaction = StudentInteraction(
            interaction_id=str(uuid.uuid4()),
            tool_type=StudentToolType.SUMMARY,
            user_input=content[:100] + "...",
            ai_response=ai_response,
            metadata={"detail_level": detail_level}
        )
        await self._add_interaction(session_id, interaction)
        return StudentToolResponse(
            interaction_id=interaction.interaction_id,
            ai_response=ai_response,
            timestamp=interaction.timestamp
        )

    async def get_history(self, session_id: str) -> List[StudentInteraction]:
        session = await self._get_session(session_id)
        return session.interactions

    async def delete_session(self, session_id: str):
        collection = database.get_collection_by_name("student_sessions")
        result = await collection.delete_one({"session_id": session_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
