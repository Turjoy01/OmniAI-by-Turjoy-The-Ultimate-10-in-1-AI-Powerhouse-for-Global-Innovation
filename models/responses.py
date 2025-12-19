"""
Response Models for Business, Social Media, and AI Agent Tools
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, List
from datetime import datetime

# ==================== BUSINESS RESPONSE MODEL ====================

class APIResponse(BaseModel):
    """Standard API response model for business tools"""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if any")

# ==================== SOCIAL MEDIA RESPONSE MODELS ====================

class CaptionResponse(BaseModel):
    """Response model for caption generation"""
    caption: str = Field(..., description="Generated caption")
    platform: str = Field(..., description="Platform the caption is for")
    
    class Config:
        json_schema_extra = {
            "example": {
                "caption": "Starting my day with the perfect cup of coffee ☕✨ There's something magical about that first sip! What's your go-to morning drink?",
                "platform": "Instagram"
            }
        }

class HashtagResponse(BaseModel):
    """Response model for hashtag generation"""
    hashtags: List[str] = Field(..., description="List of generated hashtags")
    count: int = Field(..., description="Number of hashtags generated")
    platform: str = Field(..., description="Platform the hashtags are for")
    
    class Config:
        json_schema_extra = {
            "example": {
                "hashtags": ["#fitness", "#motivation", "#workout", "#gym"],
                "count": 4,
                "platform": "Instagram"
            }
        }

class ContentIdeasResponse(BaseModel):
    """Response model for content ideas generation"""
    ideas: List[str] = Field(..., description="List of generated content ideas")
    count: int = Field(..., description="Number of ideas generated")
    platform: str = Field(..., description="Platform the ideas are for")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ideas": [
                    "[Reel] - Zero Waste Kitchen: Show your plastic-free kitchen essentials",
                    "[Carousel] - 5 Easy Swaps: Sustainable alternatives for daily items"
                ],
                "count": 2,
                "platform": "Instagram"
            }
        }

class VideoTitleResponse(BaseModel):
    """Response model for video title generation"""
    title: str = Field(..., description="Generated video title")
    platform: str = Field(..., description="Platform the title is for")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "How to Start a Podcast in 2024 | Complete Beginner's Guide",
                "platform": "YouTube"
            }
        }

class VideoDescriptionResponse(BaseModel):
    """Response model for video description generation"""
    description: str = Field(..., description="Generated video description")
    platform: str = Field(..., description="Platform the description is for")
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "Learn everything you need to know about starting a podcast...",
                "platform": "YouTube"
            }
        }

class VideoTagsResponse(BaseModel):
    """Response model for video tags generation"""
    tags: List[str] = Field(..., description="List of generated tags")
    count: int = Field(..., description="Number of tags generated")
    platform: str = Field(..., description="Platform the tags are for")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tags": ["podcast", "how to start a podcast", "podcasting tips"],
                "count": 3,
                "platform": "YouTube"
            }
        }

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid API key",
                "detail": "Please check your OPENAI_API_KEY environment variable"
            }
        }

# ==================== AI AGENT MARKETPLACE RESPONSE MODELS ====================

class AgentSuggestionResponse(BaseModel):
    """Response model for AI Agent Marketplace suggestions"""
    agent_type: str = Field(..., description="Agent type that processed the request")
    suggestions: List[str] = Field(..., description="List of tailored suggestions")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "marketing",
                "suggestions": [
                    "Focus on creating engaging content for social media.",
                    "Collaborate with influencers to boost brand awareness.",
                    "Run targeted ads to reach specific audiences."
                ]
            }
        }

# ==================== CHAT RESPONSE MODELS ====================

from typing import Literal
from bson import ObjectId

class MessageContent(BaseModel):
    """Message content model for multi-modal messages"""
    type: Literal["text", "image_url"] = Field(..., description="Content type: text or image_url")
    text: Optional[str] = Field(None, description="Text content")
    image_url: Optional[dict] = Field(None, description="Image URL data")

class Message(BaseModel):
    """Chat message model"""
    role: Literal["user", "assistant", "system"] = Field(..., description="Message role: user, assistant, or system")
    content: str | List[MessageContent] = Field(..., description="Message content (string or list of MessageContent)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")

class ChatSession(BaseModel):
    """Chat session model"""
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    title: Optional[str] = Field("New Chat", description="Session title - auto-generated from first message")
    messages: List[Message] = Field(default_factory=list, description="List of messages")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: lambda v: str(v)
        }

class SessionCreateResponse(BaseModel):
    """Response model for session creation"""
    session_id: str = Field(..., description="Created session ID")
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., description="Session title")
    message: str = Field(..., description="Response message")
    created_at: datetime = Field(..., description="Creation timestamp")

class ChatResponse(BaseModel):
    """Response model for chat messages"""
    session_id: str = Field(..., description="Session ID")
    title: str = Field(..., description="Session title")
    message: str = Field(..., description="AI response message")
    timestamp: datetime = Field(..., description="Response timestamp")

class SessionHistoryResponse(BaseModel):
    """Response model for session history"""
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., description="Session title")
    messages: List[Message] = Field(..., description="List of messages")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

# ==================== SESSION MODELS FOR BUSINESS, SOCIAL, AGENTS ====================

class Interaction(BaseModel):
    """Interaction model for storing request/response pairs"""
    request: dict = Field(..., description="Request data")
    response: dict = Field(..., description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Interaction timestamp")

class BusinessSession(BaseModel):
    """Business session model"""
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    title: Optional[str] = Field("New Business Session", description="Session title - auto-generated from first interaction")
    interactions: List[Interaction] = Field(default_factory=list, description="List of interactions")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: lambda v: str(v)
        }

class SocialSession(BaseModel):
    """Social media session model"""
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    title: Optional[str] = Field("New Social Session", description="Session title - auto-generated from first interaction")
    interactions: List[Interaction] = Field(default_factory=list, description="List of interactions")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: lambda v: str(v)
        }

class AgentSession(BaseModel):
    """AI Agent session model"""
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    title: Optional[str] = Field("New Agent Session", description="Session title - auto-generated from first interaction")
    interactions: List[Interaction] = Field(default_factory=list, description="List of interactions")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: lambda v: str(v)
        }

class GenericSessionHistoryResponse(BaseModel):
    """Generic response model for session history (Business, Social, Agents)"""
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    title: str = Field(..., description="Session title")
    interactions: List[Interaction] = Field(..., description="List of interactions")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

