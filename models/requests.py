"""
Request Models for Business, Social Media, and AI Agent Tools
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

# ==================== ENUMS ====================

class ToneEnum(str, Enum):
    """Available tone options"""
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    ENERGETIC = "energetic"
    FRIENDLY = "friendly"
    HUMOROUS = "humorous"
    INSPIRATIONAL = "inspirational"
    EDUCATIONAL = "educational"

class LengthEnum(str, Enum):
    """Available length options"""
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"

class AgentTypeEnum(str, Enum):
    """Supported AI marketplace agents"""
    MARKETING = "marketing"
    RESTAURANT = "restaurant"
    REAL_ESTATE = "real_estate"
    LEGAL = "legal"
    TEACHER = "teacher"
    FITNESS = "fitness"
    BUSINESS_PLAN_BUILDER = "business_plan_builder"
    FINANCIAL_FORECASTS = "financial_forecasts"
    INDUSTRY_RESEARCH = "industry_research"
    LIVEPLAN_ASSISTANT = "liveplan_assistant"

# ==================== BUSINESS REQUEST MODELS ====================

class AdsRequest(BaseModel):
    """Request model for advertisement generation"""
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    product_name: str = Field(..., description="Product or service name")
    target_audience: str = Field(..., description="Target audience description")
    ad_type: str = Field(..., description="Ad type: facebook, google, instagram, linkedin")
    key_features: Optional[List[str]] = Field(None, description="Key features to highlight")
    tone: Optional[str] = Field("professional", description="Tone of the ad")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "session_id": "session456",
                "product_name": "Smart Fitness Watch",
                "target_audience": "Health-conscious millennials aged 25-40",
                "ad_type": "facebook",
                "key_features": ["Heart rate monitoring", "Sleep tracking", "30-day battery life"],
                "tone": "professional"
            }
        }

class InvoiceRequest(BaseModel):
    """Request model for invoice generation"""
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    company_name: str = Field(..., description="Company name")
    client_name: str = Field(..., description="Client name")
    client_email: str = Field(..., description="Client email")
    items: List[dict] = Field(..., description="List of items with name, quantity, price")
    tax_rate: Optional[float] = Field(0.0, description="Tax rate percentage")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "session_id": "session456",
                "company_name": "Tech Solutions Inc.",
                "client_name": "John Doe",
                "client_email": "john@example.com",
                "items": [
                    {"name": "Web Development", "quantity": 40, "price": 100},
                    {"name": "UI/UX Design", "quantity": 20, "price": 80}
                ],
                "tax_rate": 10.0,
                "notes": "Payment due within 30 days"
            }
        }

class EmailRequest(BaseModel):
    """Request model for email generation"""
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    email_type: str = Field(..., description="Type: marketing, followup, cold_outreach, thank_you")
    recipient_name: Optional[str] = None
    subject: str = Field(..., description="Email subject")
    key_points: List[str] = Field(..., description="Main points to include")
    tone: Optional[str] = Field("professional", description="Email tone")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "session_id": "session456",
                "email_type": "marketing",
                "recipient_name": "Sarah Johnson",
                "subject": "Exclusive Offer: 30% Off Premium Plan",
                "key_points": [
                    "Limited time offer",
                    "Premium features included",
                    "Free trial available"
                ],
                "tone": "professional"
            }
        }

class CRMRequest(BaseModel):
    """Request model for CRM tasks"""
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    task: str = Field(..., description="Task: lead_summary, follow_up_schedule, customer_analysis")
    customer_data: dict = Field(..., description="Customer information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "session_id": "session456",
                "task": "lead_summary",
                "customer_data": {
                    "name": "ABC Corporation",
                    "industry": "Technology",
                    "contact": "contact@abc.com",
                    "interest": "Enterprise software solution",
                    "budget": "$50,000"
                }
            }
        }

class MenuRequest(BaseModel):
    """Request model for menu generation"""
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    restaurant_type: str = Field(..., description="Type: cafe, restaurant, bar, fast_food")
    cuisine: str = Field(..., description="Cuisine type")
    items_count: Optional[int] = Field(10, description="Number of menu items")
    price_range: Optional[str] = Field("medium", description="Price range: low, medium, high")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "session_id": "session456",
                "restaurant_type": "restaurant",
                "cuisine": "italian",
                "items_count": 10,
                "price_range": "medium"
            }
        }

class SEORequest(BaseModel):
    """Request model for SEO content generation"""
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    target_keyword: str = Field(..., description="Primary keyword")
    content_type: str = Field(..., description="Type: blog, product_page, landing_page")
    word_count: Optional[int] = Field(500, description="Target word count")
    include_meta: Optional[bool] = Field(True, description="Include meta tags")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "session_id": "session456",
                "target_keyword": "best digital marketing tools",
                "content_type": "blog",
                "word_count": 500,
                "include_meta": True
            }
        }

class ProductDescriptionRequest(BaseModel):
    """Request model for product description generation"""
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    product_name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    features: List[str] = Field(..., description="Product features")
    target_audience: str = Field(..., description="Target audience")
    tone: Optional[str] = Field("persuasive", description="Description tone")
    length: Optional[str] = Field("medium", description="Length: short, medium, long")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "session_id": "session456",
                "product_name": "Wireless Noise-Cancelling Headphones",
                "category": "Electronics",
                "features": [
                    "Active noise cancellation",
                    "40-hour battery life",
                    "Premium sound quality",
                    "Comfortable design"
                ],
                "target_audience": "Music enthusiasts and professionals",
                "tone": "persuasive",
                "length": "medium"
            }
        }

# ==================== SOCIAL MEDIA REQUEST MODELS ====================

def _platform_field_description() -> str:
    return (
        "Target social platform (e.g., Instagram, LinkedIn, Pinterest, "
        "YouTube, TikTok). This value can be any platform name."
    )

class CaptionRequest(BaseModel):
    """Request model for caption generation"""
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    platform: str = Field(..., min_length=2, max_length=50, description=_platform_field_description())
    topic: str = Field(..., description="Topic or theme for the caption", min_length=1)
    tone: ToneEnum = Field(default=ToneEnum.CASUAL, description="Tone of the caption")
    length: LengthEnum = Field(default=LengthEnum.MEDIUM, description="Length of the caption")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "session_id": "session456",
                "platform": "LinkedIn",
                "topic": "morning coffee routine",
                "tone": "casual",
                "length": "medium"
            }
        }

class HashtagRequest(BaseModel):
    """Request model for hashtag generation"""
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    platform: str = Field(..., min_length=2, max_length=50, description=_platform_field_description())
    topic: str = Field(..., description="Topic for hashtag generation", min_length=1)
    count: int = Field(default=10, ge=5, le=30, description="Number of hashtags to generate")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "session_id": "session456",
                "platform": "TikTok",
                "topic": "fitness motivation",
                "count": 10
            }
        }

class ContentIdeasRequest(BaseModel):
    """Request model for content ideas generation"""
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    platform: str = Field(..., min_length=2, max_length=50, description=_platform_field_description())
    niche: str = Field(..., description="Niche or industry for content ideas", min_length=1)
    count: int = Field(default=5, ge=3, le=10, description="Number of ideas to generate")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "session_id": "session456",
                "platform": "Pinterest",
                "niche": "sustainable living",
                "count": 5
            }
        }

class VideoTitleRequest(BaseModel):
    """Request model for video title generation"""
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    platform: str = Field(..., min_length=2, max_length=50, description=_platform_field_description())
    topic: str = Field(..., description="Topic for the video title", min_length=1)
    style: str = Field(default="clickable", description="Style of the title (clickable, informative, educational, entertaining)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "session_id": "session456",
                "platform": "YouTube",
                "topic": "how to start a podcast",
                "style": "clickable"
            }
        }

class VideoDescriptionRequest(BaseModel):
    """Request model for video description generation"""
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    platform: str = Field(..., min_length=2, max_length=50, description=_platform_field_description())
    topic: str = Field(..., description="Topic for the video description", min_length=1)
    length: LengthEnum = Field(default=LengthEnum.MEDIUM, description="Length of the description")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "session_id": "session456",
                "platform": "YouTube",
                "topic": "beginner's guide to photography",
                "length": "medium"
            }
        }

class VideoTagsRequest(BaseModel):
    """Request model for video tags generation"""
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    platform: str = Field(..., min_length=2, max_length=50, description=_platform_field_description())
    topic: str = Field(..., description="Topic for tag generation", min_length=1)
    count: int = Field(default=15, ge=5, le=30, description="Number of tags to generate")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "session_id": "session456",
                "platform": "Vimeo",
                "topic": "cooking healthy meals",
                "count": 15
            }
        }

# ==================== AI AGENT MARKETPLACE REQUEST MODELS ====================

class AgentSuggestionRequest(BaseModel):
    """Request model for AI Agent Marketplace suggestions"""
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    agent_type: AgentTypeEnum = Field(..., description="Type of agent (marketing, restaurant, real_estate, legal, teacher, fitness, business_plan_builder, financial_forecasts, industry_research, liveplan_assistant)")
    user_input: Optional[str] = Field(None, description="Optional user query or context")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "session_id": "session456",
                "agent_type": "marketing",
                "user_input": "how to improve my social media strategy"
            }
        }

# ==================== SESSION REQUEST MODELS ====================

class SessionCreateRequest(BaseModel):
    """Request model for session creation (used across all sections)"""
    user_id: str = Field(..., description="User ID")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123"
            }
        }

