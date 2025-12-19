from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime

class GroupType(str, Enum):
    STUDENT = "student"
    BUSINESS = "business"
    GENERAL = "general"

class GroupMessage(BaseModel):
    message_id: str
    user_id: str  # "AI" for AI messages
    content: str
    timestamp: datetime
    is_ai: bool = False

class Group(BaseModel):
    group_id: str
    name: str
    type: GroupType
    creator_id: str
    members: List[str]  # List of user_ids
    created_at: datetime = Field(default_factory=datetime.utcnow)
    messages: List[GroupMessage] = []

class GroupChatSession(BaseModel):
    session_id: str
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Request Models
class CreateSessionRequest(BaseModel):
    user_id: str # User ID is required to create a session

class GroupCreateRequest(BaseModel):
    user_id: str
    session_id: str # Added session_id
    name: str
    type: GroupType

class GroupJoinRequest(BaseModel):
    user_id: str
    session_id: str # Added session_id
    group_id: str

class GroupMessageRequest(BaseModel):
    user_id: str
    session_id: str # Added session_id
    group_id: str
    content: str

# Response Models
class SessionResponse(BaseModel):
    session_id: str # Added session_id
    user_id: str
    message: str

class GroupResponse(BaseModel):
    group_id: str
    name: str
    type: GroupType
    member_count: int
    message: str

class GroupHistoryResponse(BaseModel):
    group_id: str
    name: str
    messages: List[GroupMessage]
