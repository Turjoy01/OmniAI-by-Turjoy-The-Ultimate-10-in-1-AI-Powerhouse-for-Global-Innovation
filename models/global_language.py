from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum

class InteractionType(str, Enum):
    CHAT = "chat"
    VOICE = "voice"

class Interaction(BaseModel):
    interaction_id: str
    type: InteractionType
    user_input: str  # Text prompt or transcribed text
    ai_response: str # AI Text response
    target_language: str
    audio_url: Optional[str] = None # For voice interactions
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class GlobalSession(BaseModel):
    session_id: str
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    interactions: List[Interaction] = []

# Request Models
class CreateSessionRequest(BaseModel):
    user_id: str

class ChatRequest(BaseModel):
    session_id: str
    user_id: str
    message: str
    target_language: str = "English"

# Voice Request is typically handled via Multipart/Form-data, so pydantic model might not be directly used for the body,
# but we can define a response model.

# Response Models
class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response_text: str
    target_language: str

class VoiceResponse(BaseModel):
    transcription: str
    response_text: str
    audio_base64: str # Returning base64 audio for simplicity in this API
    target_language: str
    
class HistoryResponse(BaseModel):
    session_id: str
    interactions: List[Interaction]
