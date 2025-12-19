from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, Response
from typing import List

from models.global_language import (
    CreateSessionRequest, SessionResponse,
    ChatRequest, ChatResponse,
    VoiceResponse, HistoryResponse,
    Interaction
)
from services.global_language_service import GlobalLanguageService

# Initialize router
global_language_router = APIRouter(prefix="/api/global-language", tags=["Global Language Support"])

# Initialize service
service = GlobalLanguageService()

@global_language_router.post("/session/create", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(request: CreateSessionRequest):
    """
    Create a new Global Language Session.
    Returns session_id.
    """
    try:
        session_id = await service.create_session(user_id=request.user_id)
        return SessionResponse(
            session_id=session_id,
            user_id=request.user_id,
            message="Global Language Session created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@global_language_router.post("/voice", response_model=VoiceResponse)
async def process_voice(
    session_id: str = Form(...),
    user_id: str = Form(...),
    target_language: str = Form("English"),
    audio_file: UploadFile = File(...)
):
    """
    Process Voice Interaction (JSON Response).
    - Returns: Transcribed Text, Response Text, Response Audio (Base64)
    """
    try:
        # Read audio file
        audio_data = await audio_file.read()
        
        result = await service.process_voice_interaction(
            session_id=session_id,
            user_id=user_id,
            audio_data=audio_data,
            target_language=target_language
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@global_language_router.post("/voice/file")
async def process_voice_file(
    session_id: str = Form(...),
    user_id: str = Form(...),
    target_language: str = Form("English"),
    audio_file: UploadFile = File(...)
):
    """
    Process Voice Interaction (Direct File Response).
    - Returns: Audio File (audio/mpeg) directly downloadable/playable.
    """
    try:
        # Read audio file
        audio_data = await audio_file.read()
        
        audio_bytes = await service.process_voice_interaction_file(
            session_id=session_id,
            user_id=user_id,
            audio_data=audio_data,
            target_language=target_language
        )
        
        return Response(
            content=audio_bytes, 
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=response.mp3",
                "Content-Length": str(len(audio_bytes))
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@global_language_router.post("/chat", response_model=ChatResponse)
async def process_chat(request: ChatRequest):
    """
    Process Multilingual Chat Interaction.
    - Input: Text + Target Language
    - AI answers in Target Language
    """
    try:
        result = await service.process_chat_interaction(
            session_id=request.session_id,
            user_id=request.user_id,
            message=request.message,
            target_language=request.target_language
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@global_language_router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(session_id: str):
    """
    Get session interaction history.
    """
    try:
        interactions = await service.get_history(session_id)
        return HistoryResponse(
            session_id=session_id,
            interactions=interactions
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@global_language_router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session.
    """
    try:
        await service.delete_session(session_id)
        return {"message": "Session deleted successfully", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
