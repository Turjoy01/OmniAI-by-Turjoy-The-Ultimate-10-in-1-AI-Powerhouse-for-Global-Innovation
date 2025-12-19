from fastapi import APIRouter, HTTPException, status
from typing import List
import uuid

from models.group_chat import (
    CreateSessionRequest,
    SessionResponse,
    GroupCreateRequest,
    GroupJoinRequest,
    GroupMessageRequest,
    GroupResponse,
    GroupHistoryResponse,
    GroupMessage,
    GroupType
)
from services.group_chat_service import GroupChatService

# Initialize router
group_chat_router = APIRouter(prefix="/api/group-chat", tags=["Group Chat"])

# Initialize service
group_chat_service = GroupChatService()

@group_chat_router.post("/session/create", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(request: CreateSessionRequest):
    """
    Create a new User Session.
    Returns: unique session_id to be used in subsequent requests.
    """
    try:
        session_id = await group_chat_service.create_session(user_id=request.user_id)
        return SessionResponse(
            session_id=session_id,
            user_id=request.user_id,
            message="Session created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@group_chat_router.post("/group/create", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(request: GroupCreateRequest):
    """
    Create a new group (Student, Business, or General).
    Requires valid session_id.
    """
    try:
        group = await group_chat_service.create_group(
            user_id=request.user_id,
            session_id=request.session_id,
            name=request.name,
            group_type=request.type
        )
        return GroupResponse(
            group_id=group.group_id,
            name=group.name,
            type=group.type,
            member_count=len(group.members),
            message=f"{group.type.value} group created successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@group_chat_router.post("/group/join", response_model=GroupResponse)
async def join_group(request: GroupJoinRequest):
    """
    Join an existing group using its ID.
    Requires valid session_id.
    """
    try:
        group = await group_chat_service.join_group(
            user_id=request.user_id,
            session_id=request.session_id,
            group_id=request.group_id
        )
        return GroupResponse(
            group_id=group.group_id,
            name=group.name,
            type=group.type,
            member_count=len(group.members),
            message="Joined group successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@group_chat_router.post("/group/message", response_model=GroupMessage)
async def send_message(request: GroupMessageRequest):
    """
    Send a message to the group. 
    Requires valid session_id.
    """
    try:
        ai_message = await group_chat_service.send_message(
            group_id=request.group_id,
            session_id=request.session_id,
            user_id=request.user_id,
            content=request.content
        )
        return ai_message
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@group_chat_router.get("/group/history/{group_id}", response_model=List[GroupMessage])
async def get_history(group_id: str):
    """
    Get the chat history of a group.
    """
    try:
        messages = await group_chat_service.get_group_history(group_id)
        return messages
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@group_chat_router.delete("/group/{group_id}")
async def delete_group(group_id: str, user_id: str):
    """
    Delete a group. Only the creator can delete it.
    """
    try:
        await group_chat_service.delete_group(group_id, user_id)
        return {"message": "Group deleted successfully", "group_id": group_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
