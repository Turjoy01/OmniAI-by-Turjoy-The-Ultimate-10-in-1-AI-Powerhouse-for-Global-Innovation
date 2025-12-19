"""
Social Media Tools Routes

All social media-related API endpoints with session management.
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import uuid

from models.requests import (
    CaptionRequest,
    HashtagRequest,
    ContentIdeasRequest,
    VideoTitleRequest,
    VideoDescriptionRequest,
    VideoTagsRequest,
    SessionCreateRequest,
)
from models.responses import (
    CaptionResponse,
    HashtagResponse,
    ContentIdeasResponse,
    VideoTitleResponse,
    VideoDescriptionResponse,
    VideoTagsResponse,
    SessionCreateResponse,
    SocialSession,
    Interaction,
    GenericSessionHistoryResponse,
)
from services.social_services import ContentGeneratorService
from services.database import database
from services.openai_service import OpenAIService

# Initialize router
social_router = APIRouter(prefix="/api/social", tags=["Social Media Tools"])

# Initialize service
content_service = ContentGeneratorService()
openai_service = OpenAIService()


# ==================== SESSION MANAGEMENT ENDPOINTS ====================

@social_router.post("/session/create", response_model=SessionCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_social_session(user_id: str):
    """
    Create a new social media session
    
    **Step 1:** Call this endpoint to create a session
    - Provide: user_id
    - Returns: session_id
    
    The session will start with title "New Social Session" - it will be auto-updated 
    after the first interaction based on the social media tool used.
    
    Use this session_id for all subsequent social media tool requests.
    """
    try:
        collection = database.get_collection_by_name("social_sessions")
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Create new session with default title
        social_session = SocialSession(
            session_id=session_id,
            user_id=user_id,
            title="New Social Session",
            interactions=[]
        )
        
        # Save to MongoDB
        await collection.insert_one(social_session.model_dump())
        
        return SessionCreateResponse(
            session_id=session_id,
            user_id=user_id,
            title=social_session.title,
            message="Social media session created successfully",
            created_at=social_session.created_at
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create social media session: {str(e)}"
        )

# ==================== HELPER FUNCTION ====================

async def save_social_interaction(
    user_id: str,
    session_id: str,
    request_data: dict,
    response_data: dict,
    tool_name: str
):
    """
    Save a social media interaction to the session and generate title if first interaction
    
    Args:
        user_id: User ID
        session_id: Session ID
        request_data: Request data dictionary
        response_data: Response data dictionary
        tool_name: Name of the social media tool used
    """
    collection = database.get_collection_by_name("social_sessions")
    
    # Find session
    session = await collection.find_one({
        "session_id": session_id,
        "user_id": user_id
    })
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Social media session not found or does not belong to user"
        )
    
    social_session = SocialSession(**session)
    
    # Check if this is the first interaction (for title generation)
    is_first_interaction = len(social_session.interactions) == 0
    
    # Generate title from first interaction
    if is_first_interaction:
        try:
            # Create a descriptive prompt based on the tool and request
            platform = request_data.get("platform", "")
            topic = request_data.get("topic", "") or request_data.get("niche", "")
            title_prompt = f"{platform} {tool_name}: {topic}"
            generated_title = await openai_service.generate_title(title_prompt)
            social_session.title = generated_title
        except Exception as e:
            # Fallback title if generation fails
            platform = request_data.get("platform", "Social")
            social_session.title = f"{platform} {tool_name}"
    
    # Create interaction
    interaction = Interaction(
        request=request_data,
        response=response_data,
        timestamp=datetime.utcnow()
    )
    
    # Add interaction to session
    social_session.interactions.append(interaction)
    social_session.updated_at = datetime.utcnow()
    
    # Save to MongoDB
    await collection.update_one(
        {"session_id": session_id, "user_id": user_id},
        {"$set": social_session.model_dump()},
        upsert=True
    )
    
    return social_session.title


# ==================== SOCIAL MEDIA TOOL ENDPOINTS ====================

@social_router.post("/caption", response_model=CaptionResponse)
async def generate_caption(request: CaptionRequest):
    """
    Generate a caption for any social platform
    
    - **user_id**: User ID
    - **session_id**: Session ID from /session/create
    - **platform**: Target social platform
    - **topic**: Topic or theme for the caption
    - **tone**: Tone of the caption
    - **length**: Length of the caption
    """
    try:
        caption = await content_service.generate_caption(
            platform=request.platform,
            topic=request.topic,
            tone=request.tone.value,
            length=request.length.value,
        )
        
        # Save interaction to session
        title = await save_social_interaction(
            user_id=request.user_id,
            session_id=request.session_id,
            request_data=request.model_dump(),
            response_data={"caption": caption, "platform": request.platform},
            tool_name="Caption"
        )
        
        return CaptionResponse(
            caption=caption,
            platform=request.platform
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate caption: {exc}")


@social_router.post("/hashtags", response_model=HashtagResponse)
async def generate_hashtags(request: HashtagRequest):
    """
    Generate hashtags for any platform
    
    - **user_id**: User ID
    - **session_id**: Session ID from /session/create
    - **platform**: Target social platform
    - **topic**: Topic for hashtag generation
    - **count**: Number of hashtags to generate
    """
    try:
        hashtags = await content_service.generate_hashtags(
            platform=request.platform,
            topic=request.topic,
            count=request.count,
        )
        
        # Save interaction to session
        title = await save_social_interaction(
            user_id=request.user_id,
            session_id=request.session_id,
            request_data=request.model_dump(),
            response_data={"hashtags": hashtags, "count": len(hashtags), "platform": request.platform},
            tool_name="Hashtags"
        )
        
        return HashtagResponse(
            hashtags=hashtags,
            count=len(hashtags),
            platform=request.platform
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate hashtags: {exc}")


@social_router.post("/content-ideas", response_model=ContentIdeasResponse)
async def generate_content_ideas(request: ContentIdeasRequest):
    """
    Generate content ideas tailored to the specified platform
    
    - **user_id**: User ID
    - **session_id**: Session ID from /session/create
    - **platform**: Target social platform
    - **niche**: Niche or industry for content ideas
    - **count**: Number of ideas to generate
    """
    try:
        ideas = await content_service.generate_content_ideas(
            platform=request.platform,
            niche=request.niche,
            count=request.count,
        )
        
        # Save interaction to session
        title = await save_social_interaction(
            user_id=request.user_id,
            session_id=request.session_id,
            request_data=request.model_dump(),
            response_data={"ideas": ideas, "count": len(ideas), "platform": request.platform},
            tool_name="Content Ideas"
        )
        
        return ContentIdeasResponse(
            ideas=ideas,
            count=len(ideas),
            platform=request.platform
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate content ideas: {exc}")


@social_router.post("/video/title", response_model=VideoTitleResponse)
async def generate_video_title(request: VideoTitleRequest):
    """
    Generate a video title for any video-first platform
    
    - **user_id**: User ID
    - **session_id**: Session ID from /session/create
    - **platform**: Target social platform
    - **topic**: Topic for the video title
    - **style**: Style of the title
    """
    try:
        title_text = await content_service.generate_video_title(
            platform=request.platform,
            topic=request.topic,
            style=request.style,
        )
        
        # Save interaction to session
        session_title = await save_social_interaction(
            user_id=request.user_id,
            session_id=request.session_id,
            request_data=request.model_dump(),
            response_data={"title": title_text, "platform": request.platform},
            tool_name="Video Title"
        )
        
        return VideoTitleResponse(
            title=title_text,
            platform=request.platform
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate video title: {exc}")


@social_router.post("/video/description", response_model=VideoDescriptionResponse)
async def generate_video_description(request: VideoDescriptionRequest):
    """
    Generate a video description for any video-first platform
    
    - **user_id**: User ID
    - **session_id**: Session ID from /session/create
    - **platform**: Target social platform
    - **topic**: Topic for the video description
    - **length**: Length of the description
    """
    try:
        description = await content_service.generate_video_description(
            platform=request.platform,
            topic=request.topic,
            length=request.length.value,
        )
        
        # Save interaction to session
        title = await save_social_interaction(
            user_id=request.user_id,
            session_id=request.session_id,
            request_data=request.model_dump(),
            response_data={"description": description, "platform": request.platform},
            tool_name="Video Description"
        )
        
        return VideoDescriptionResponse(
            description=description,
            platform=request.platform
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate video description: {exc}")


@social_router.post("/video/tags", response_model=VideoTagsResponse)
async def generate_video_tags(request: VideoTagsRequest):
    """
    Generate video tags for any platform
    
    - **user_id**: User ID
    - **session_id**: Session ID from /session/create
    - **platform**: Target social platform
    - **topic**: Topic for tag generation
    - **count**: Number of tags to generate
    """
    try:
        tags = await content_service.generate_video_tags(
            platform=request.platform,
            topic=request.topic,
            count=request.count,
        )
        
        # Save interaction to session
        title = await save_social_interaction(
            user_id=request.user_id,
            session_id=request.session_id,
            request_data=request.model_dump(),
            response_data={"tags": tags, "count": len(tags), "platform": request.platform},
            tool_name="Video Tags"
        )
        
        return VideoTagsResponse(
            tags=tags,
            count=len(tags),
            platform=request.platform
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate video tags: {exc}")


@social_router.get("/history/{session_id}", response_model=GenericSessionHistoryResponse, status_code=status.HTTP_200_OK)
async def get_social_session_history(
    session_id: str,
    user_id: str
):
    """
    Get social media session history
    
    **Parameters:**
    - session_id: The session ID (path parameter)
    - user_id: Your user ID (query parameter)
    
    **Returns:** All interactions in this social media session with the session title
    """
    try:
        collection = database.get_collection_by_name("social_sessions")
        
        # Find session
        session = await collection.find_one({
            "session_id": session_id,
            "user_id": user_id
        })
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Social media session not found or does not belong to user"
            )
        
        social_session = SocialSession(**session)
        
        return GenericSessionHistoryResponse(
            session_id=social_session.session_id,
            user_id=social_session.user_id,
            title=social_session.title,
            interactions=social_session.interactions,
            created_at=social_session.created_at,
            updated_at=social_session.updated_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve social media session history: {str(e)}"
        )


@social_router.delete("/session/{session_id}", status_code=status.HTTP_200_OK)
async def delete_social_session(
    session_id: str,
    user_id: str
):
    """
    Delete a specific social media session
    
    **Parameters:**
    - session_id: The session to delete (path parameter)
    - user_id: Your user ID (query parameter)
    
    **Security:** Only the session owner can delete it
    """
    try:
        collection = database.get_collection_by_name("social_sessions")
        
        # Delete session (only if belongs to user)
        result = await collection.delete_one({
            "session_id": session_id,
            "user_id": user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Social media session not found or does not belong to user"
            )
        
        return {
            "message": "Social media session deleted successfully",
            "session_id": session_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete social media session: {str(e)}"
        )


@social_router.get("/sessions/list", status_code=status.HTTP_200_OK)
async def list_social_sessions(user_id: str):
    """
    List all social media sessions for a user
    
    **Parameters:**
    - user_id: Your user ID (query parameter)
    
    **Returns:** List of all social media sessions with title, interaction count, and timestamps
    """
    try:
        collection = database.get_collection_by_name("social_sessions")
        
        # Find all sessions for user
        cursor = collection.find(
            {"user_id": user_id},
            {"session_id": 1, "title": 1, "created_at": 1, "updated_at": 1, "interactions": 1, "_id": 0}
        ).sort("updated_at", -1)
        
        sessions = await cursor.to_list(length=None)
        
        # Add interaction count and title to each session
        session_list = []
        for session in sessions:
            session_list.append({
                "session_id": session["session_id"],
                "title": session.get("title", "New Social Session"),
                "interaction_count": len(session.get("interactions", [])),
                "created_at": session["created_at"],
                "updated_at": session["updated_at"]
            })
        
        return {
            "user_id": user_id,
            "total_sessions": len(session_list),
            "sessions": session_list
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list social media sessions: {str(e)}"
        )
