import logging
import os
import uuid
import base64
import datetime
from typing import List, Optional
from fastapi import HTTPException

from models.global_language import (
    GlobalSession, Interaction, InteractionType,
    VoiceResponse, ChatResponse
)
from services.database import database
from services.openai_service import OpenAIService

# Configure logging to file
log_path = os.path.join(os.getcwd(), "global_language_service.log")
logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
print(f"DEBUG: Logging initialized at {log_path}")

class GlobalLanguageService:
    def __init__(self):
        self.openai_service = OpenAIService()

    async def create_session(self, user_id: str) -> str:
        """Create a new global language session"""
        collection = database.get_collection_by_name("global_language_sessions")
        session_id = str(uuid.uuid4())
        
        session = GlobalSession(
            session_id=session_id,
            user_id=user_id,
        )
        await collection.insert_one(session.model_dump())
        logger.info(f"Created session: {session_id} for user: {user_id}")
        return session_id

    async def _get_session(self, session_id: str) -> GlobalSession:
        """Retrieve a session by ID or raise 404"""
        collection = database.get_collection_by_name("global_language_sessions")
        data = await collection.find_one({"session_id": session_id})
        if not data:
            raise HTTPException(status_code=404, detail="Session not found")
        return GlobalSession(**data)

    async def _add_interaction(self, session_id: str, interaction: Interaction):
        """Add interaction to session history"""
        collection = database.get_collection_by_name("global_language_sessions")
        await collection.update_one(
            {"session_id": session_id},
            {"$push": {"interactions": interaction.model_dump()}}
        )

    async def process_voice_interaction(self, session_id: str, user_id: str, audio_data: bytes, target_language: str) -> VoiceResponse:
        """
        Process voice input:
        1. Transcribe Audio (Whisper)
        2. Generate AI Answer in Target Language (GPT-4o)
        3. Convert Answer to Audio (TTS)
        """
        logger.info(f"Processing voice (JSON) for session: {session_id}")
        # Validate Session
        await self._get_session(session_id)

        # 1. Transcribe
        try:
            transcription = await self.openai_service.transcribe_audio(audio_data)
            logger.debug(f"Transcription: {transcription}")
        except Exception as e:
            logger.error(f"Transcription Error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

        # 2. AI Answer
        system_prompt = f"You are a helpful assistant. The user is speaking. Answer their question directly in {target_language} language. Keep the answer concise and conversational."
        
        if not transcription.strip():
            ai_text_response = "I couldn't hear you clearly. Could you please repeat that?"
            logger.warning("Empty transcription, using fallback response")
        else:
            try:
                ai_text_response = await self.openai_service.chat_completion(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": transcription}
                    ],
                    max_tokens=300
                )
                logger.debug(f"AI Response: {ai_text_response}")
            except Exception as e:
                logger.error(f"AI Error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"AI Response generation failed: {str(e)}")

        # 3. Text to Speech
        try:
            audio_bytes = await self.openai_service.generate_audio(ai_text_response)
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            logger.debug(f"TTS complete: {len(audio_bytes)} bytes")
        except Exception as e:
            logger.error(f"TTS Error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")

        # 4. Save Interaction
        interaction = Interaction(
            interaction_id=str(uuid.uuid4()),
            type=InteractionType.VOICE,
            user_input=transcription,
            ai_response=ai_text_response,
            target_language=target_language,
            audio_url="[BINARY_DATA]"
        )
        await self._add_interaction(session_id, interaction)

        return VoiceResponse(
            transcription=transcription,
            response_text=ai_text_response,
            audio_base64=audio_base64,
            target_language=target_language
        )

    async def process_chat_interaction(self, session_id: str, user_id: str, message: str, target_language: str) -> ChatResponse:
        """
        Process text chat:
        1. Generate AI Answer in Target Language
        """
        logger.info(f"Processing chat for session: {session_id}")
        # Validate Session
        await self._get_session(session_id)

        system_prompt = f"You are a helpful assistant. Answer the user's question directly in {target_language} language."
        
        try:
            ai_text_response = await self.openai_service.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=500
            )
            logger.debug(f"AI Response: {ai_text_response}")
        except Exception as e:
            logger.error(f"AI Error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"AI Response generation failed: {str(e)}")

        # Save Interaction
        interaction = Interaction(
            interaction_id=str(uuid.uuid4()),
            type=InteractionType.CHAT,
            user_input=message,
            ai_response=ai_text_response,
            target_language=target_language
        )
        await self._add_interaction(session_id, interaction)

        return ChatResponse(
            response_text=ai_text_response,
            target_language=target_language
        )

    async def get_history(self, session_id: str) -> List[Interaction]:
        session = await self._get_session(session_id)
        return session.interactions

    async def delete_session(self, session_id: str):
        collection = database.get_collection_by_name("global_language_sessions")
        result = await collection.delete_one({"session_id": session_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        logger.info(f"Deleted session: {session_id}")

    async def process_voice_interaction_file(self, session_id: str, user_id: str, audio_data: bytes, target_language: str) -> bytes:
        """
        Process voice input and return Binary Audio directly.
        """
        logger.info(f"Processing voice (FILE) for session: {session_id}")
        # Validate Session
        await self._get_session(session_id)

        # 1. Transcribe
        try:
            transcription = await self.openai_service.transcribe_audio(audio_data)
            logger.debug(f"Transcription: {transcription}")
        except Exception as e:
            logger.error(f"Transcription Error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

        # 2. AI Answer
        system_prompt = f"You are a helpful assistant. The user is speaking. Answer their question directly in {target_language} language. Keep the answer concise and conversational."
        
        if not transcription.strip():
            ai_text_response = "I couldn't hear you clearly. Could you please repeat that?"
            logger.warning("Empty transcription, using fallback response")
        else:
            try:
                ai_text_response = await self.openai_service.chat_completion(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": transcription}
                    ],
                    max_tokens=300
                )
                logger.debug(f"AI Response: {ai_text_response}")
            except Exception as e:
                logger.error(f"AI Error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"AI Response generation failed: {str(e)}")

        # 3. Text to Speech
        try:
            audio_bytes = await self.openai_service.generate_audio(ai_text_response)
            logger.debug(f"TTS complete: {len(audio_bytes)} bytes")
        except Exception as e:
            logger.error(f"TTS Error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")

        # 4. Save Interaction
        interaction = Interaction(
            interaction_id=str(uuid.uuid4()),
            type=InteractionType.VOICE,
            user_input=transcription,
            ai_response=ai_text_response,
            target_language=target_language,
            audio_url="[BINARY_FILE_RETURNED]" 
        )
        await self._add_interaction(session_id, interaction)

        return audio_bytes
