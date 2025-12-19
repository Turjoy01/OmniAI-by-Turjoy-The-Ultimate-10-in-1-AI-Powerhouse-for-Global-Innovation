"""
AI Agents Marketplace Routes

Provides a unified endpoint for all AI marketplace agents with session management.
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import uuid

from models.requests import AgentSuggestionRequest, SessionCreateRequest
from models.responses import (
    AgentSuggestionResponse,
    SessionCreateResponse,
    AgentSession,
    Interaction,
    GenericSessionHistoryResponse,
)
from services import AgentsService
from services.database import database
from services.openai_service import OpenAIService

agents_router = APIRouter(prefix="/api/agents", tags=["AI Agents Marketplace"])
agents_service = AgentsService()
openai_service = OpenAIService()


# ==================== SESSION MANAGEMENT ENDPOINTS ====================

@agents_router.post("/session/create", response_model=SessionCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_agent_session(user_id: str):
    """
    Create a new AI agent session
    
    **Step 1:** Call this endpoint to create a session
    - Provide: user_id
    - Returns: session_id
    
    The session will start with title "New Agent Session" - it will be auto-updated 
    after the first interaction based on the agent type used.
    
    Use this session_id for all subsequent AI agent requests.
    """
    try:
        collection = database.get_collection_by_name("agents_sessions")
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Create new session with default title
        agent_session = AgentSession(
            session_id=session_id,
            user_id=user_id,
            title="New Agent Session",
            interactions=[]
        )
        
        # Save to MongoDB
        await collection.insert_one(agent_session.model_dump())
        
        return SessionCreateResponse(
            session_id=session_id,
            user_id=user_id,
            title=agent_session.title,
            message="AI agent session created successfully",
            created_at=agent_session.created_at
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create AI agent session: {str(e)}"
        )

# ==================== HELPER FUNCTION ====================

async def save_agent_interaction(
    user_id: str,
    session_id: str,
    request_data: dict,
    response_data: dict,
    agent_type: str
):
    """
    Save an AI agent interaction to the session and generate title if first interaction
    
    Args:
        user_id: User ID
        session_id: Session ID
        request_data: Request data dictionary
        response_data: Response data dictionary
        agent_type: Type of AI agent used
    """
    collection = database.get_collection_by_name("agents_sessions")
    
    # Find session
    session = await collection.find_one({
        "session_id": session_id,
        "user_id": user_id
    })
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI agent session not found or does not belong to user"
        )
    
    agent_session = AgentSession(**session)
    
    # Check if this is the first interaction (for title generation)
    is_first_interaction = len(agent_session.interactions) == 0
    
    # Generate title from first interaction
    if is_first_interaction:
        try:
            # Create a descriptive prompt based on the agent type and user input
            user_input = request_data.get("user_input", "")
            if user_input:
                title_prompt = f"{agent_type} Agent: {user_input}"
            else:
                title_prompt = f"{agent_type} Agent Session"
            generated_title = await openai_service.generate_title(title_prompt)
            agent_session.title = generated_title
        except Exception as e:
            # Fallback title if generation fails
            agent_session.title = f"{agent_type.replace('_', ' ').title()} Agent"
    
    # Create interaction
    interaction = Interaction(
        request=request_data,
        response=response_data,
        timestamp=datetime.utcnow()
    )
    
    # Add interaction to session
    agent_session.interactions.append(interaction)
    agent_session.updated_at = datetime.utcnow()
    
    # Save to MongoDB
    await collection.update_one(
        {"session_id": session_id, "user_id": user_id},
        {"$set": agent_session.model_dump()},
        upsert=True
    )
    
    return agent_session.title


# ==================== AI AGENT ENDPOINT ====================

@agents_router.post("/suggestions", response_model=AgentSuggestionResponse)
async def get_agent_suggestions(request: AgentSuggestionRequest):
    """
    Get AI-powered tailored suggestions from specialized agents
    
    - **user_id**: User ID
    - **session_id**: Session ID from /session/create
    - **agent_type**: Type of agent (marketing, restaurant, real_estate, legal, teacher, fitness, business_plan_builder, financial_forecasts, industry_research, liveplan_assistant)
    - **user_input**: Optional user query or context to personalize suggestions
    """
    try:
        suggestions = await agents_service.get_suggestions(
            agent_type=request.agent_type,
            user_input=request.user_input,
        )
        
        # Save interaction to session
        title = await save_agent_interaction(
            user_id=request.user_id,
            session_id=request.session_id,
            request_data=request.model_dump(),
            response_data={"agent_type": request.agent_type, "suggestions": suggestions},
            agent_type=request.agent_type
        )
        
        return AgentSuggestionResponse(
            agent_type=request.agent_type,
            suggestions=suggestions,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate suggestions: {exc}")
    




@agents_router.get("/history/{session_id}", response_model=GenericSessionHistoryResponse, status_code=status.HTTP_200_OK)
async def get_agent_session_history(
    session_id: str,
    user_id: str
):
    """
    Get AI agent session history
    
    **Parameters:**
    - session_id: The session ID (path parameter)
    - user_id: Your user ID (query parameter)
    
    **Returns:** All interactions in this AI agent session with the session title
    """
    try:
        collection = database.get_collection_by_name("agents_sessions")
        
        # Find session
        session = await collection.find_one({
            "session_id": session_id,
            "user_id": user_id
        })
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI agent session not found or does not belong to user"
            )
        
        agent_session = AgentSession(**session)
        
        return GenericSessionHistoryResponse(
            session_id=agent_session.session_id,
            user_id=agent_session.user_id,
            title=agent_session.title,
            interactions=agent_session.interactions,
            created_at=agent_session.created_at,
            updated_at=agent_session.updated_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve AI agent session history: {str(e)}"
        )


@agents_router.delete("/session/{session_id}", status_code=status.HTTP_200_OK)
async def delete_agent_session(
    session_id: str,
    user_id: str
):
    """
    Delete a specific AI agent session
    
    **Parameters:**
    - session_id: The session to delete (path parameter)
    - user_id: Your user ID (query parameter)
    
    **Security:** Only the session owner can delete it
    """
    try:
        collection = database.get_collection_by_name("agents_sessions")
        
        # Delete session (only if belongs to user)
        result = await collection.delete_one({
            "session_id": session_id,
            "user_id": user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI agent session not found or does not belong to user"
            )
        
        return {
            "message": "AI agent session deleted successfully",
            "session_id": session_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete AI agent session: {str(e)}"
        )



@agents_router.get("/sessions/list", status_code=status.HTTP_200_OK)
async def list_agent_sessions(user_id: str):
    """
    List all AI agent sessions for a user
    
    **Parameters:**
    - user_id: Your user ID (query parameter)
    
    **Returns:** List of all AI agent sessions with title, interaction count, and timestamps
    """
    try:
        collection = database.get_collection_by_name("agents_sessions")
        
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
                "title": session.get("title", "New Agent Session"),
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
            detail=f"Failed to list AI agent sessions: {str(e)}"
        )
