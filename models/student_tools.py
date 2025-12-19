from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum

class StudentToolType(str, Enum):
    HOMEWORK = "homework"
    ESSAY = "essay"
    MATH = "math"
    STUDY = "study"
    FLASHCARDS = "flashcards"
    SUMMARY = "summary"

class StudentInteraction(BaseModel):
    interaction_id: str
    tool_type: StudentToolType
    user_input: str
    ai_response: str
    metadata: Optional[dict] = None  # To store subject, topic, tone, etc.
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StudentSession(BaseModel):
    session_id: str
    user_id: str
    interactions: List[StudentInteraction] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Request Models
class CreateSessionRequest(BaseModel):
    user_id: str

class HomeworkRequest(BaseModel):
    session_id: str
    user_id: str
    subject: str
    question: str

class EssayRequest(BaseModel):
    session_id: str
    user_id: str
    topic: str
    length: Literal["short", "medium", "long"] = "medium"
    tone: Literal["academic", "persuasive", "narrative", "descriptive"] = "academic"

class MathRequest(BaseModel):
    session_id: str
    user_id: str
    problem: str

class StudyRequest(BaseModel):
    session_id: str
    user_id: str
    topic: str
    question: Optional[str] = None # For continuing the study session

class FlashcardsRequest(BaseModel):
    session_id: str
    user_id: str
    content: str
    format: Literal["pairs", "cloze"] = "pairs"

class SummaryRequest(BaseModel):
    session_id: str
    user_id: str
    content: str
    detail_level: Literal["concise", "detailed", "bullet_points"] = "detailed"

# Response Models
class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    message: str

class StudentToolResponse(BaseModel):
    interaction_id: str
    ai_response: str
    timestamp: datetime

class HistoryResponse(BaseModel):
    session_id: str
    interactions: List[StudentInteraction]
