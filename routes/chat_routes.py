from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, Request
from typing import Optional, Union
from datetime import datetime
import uuid
import base64

from models.responses import (
    SessionCreateResponse,
    ChatResponse, 
    SessionHistoryResponse, 
    ChatSession, 
    Message,
    MessageContent
)
from services.database import database
from services.openai_service import OpenAIService
from utils.audio_processing import validate_image_url

chat_router = APIRouter(prefix="/api/chat", tags=["Chat"])
openai_service = OpenAIService()


@chat_router.post("/session/create", response_model=SessionCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_session(user_id: str = Form(..., description="User ID")):
    """
    Create a new chat session
    
    **Step 1:** Call this endpoint to create a session
    - Provide: user_id
    - Returns: session_id
    
    The session will start with title "New Chat" - it will be auto-updated 
    after the first message based on conversation context.
    
    Use this session_id for all subsequent messages.
    """
    try:
        collection = database.get_collection()
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Create new session with default title
        chat_session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            title="New Chat",  # Will be updated after first message
            messages=[]
        )
        
        # Save to MongoDB
        await collection.insert_one(chat_session.model_dump())
        
        return SessionCreateResponse(
            session_id=session_id,
            user_id=user_id,
            title=chat_session.title,
            message="Session created successfully",
            created_at=chat_session.created_at
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


def extract_text_from_content(content) -> str:
    """
    Extract text from message content (handles both string and list formats)
    """
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        # Extract text from multi-modal content
        text_parts = []
        for item in content:
            if isinstance(item, MessageContent) and item.type == "text" and item.text:
                text_parts.append(item.text)
            elif isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        return " ".join(text_parts)
    return ""



@chat_router.post("/message", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def send_message(
    user_id: str = Form(..., description="User ID"),
    session_id: str = Form(..., description="Session ID from /session/create"),
    message: str = Form("", description="Text message (optional if audio/image provided)"),
    audio: Union[UploadFile, str, None] = File(None, description="Audio file - auto converts to text"),
    image: Union[UploadFile, str, None] = File(None, description="Image file upload")
):
    """
    Send a message with text, voice, and/or image
    
    **Step 2:** Send messages to this endpoint
    
    **Auto Title Generation:**
    - First message in a session automatically generates a short title
    - Title is based on the conversation context (2-6 words)
    - Title remains fixed for the entire session
    - Subsequent messages don't change the title
    
    **Supports:**
    - Text messages
    - Voice-to-text (audio file → automatically transcribed)
    - Image upload from device
    - Or any combination of above
    
    **Voice Recording Flow:**
    1. Record audio in your app
    2. Send audio file here
    3. Backend auto-transcribes to text
    4. Text gets sent to ChatGPT
    
    **Requirements:**
    - user_id: Your user identifier
    - session_id: From /session/create endpoint
    - At least one of: message, audio, or image
    """
    try:
        # Debug logging
        print(f"DEBUG: message='{message}'")
        print(f"DEBUG: audio type={type(audio)}, value={audio}")
        print(f"DEBUG: image type={type(image)}, value={image}")

        # Normalize inputs - handle string values from empty form fields
        if isinstance(audio, str):
            print("DEBUG: Normalizing audio string to None")
            audio = None
        if isinstance(image, str):
            print("DEBUG: Normalizing image string to None")
            image = None

        collection = database.get_collection()
        
        # Verify session exists and belongs to user
        session = await collection.find_one({
            "session_id": session_id,
            "user_id": user_id
        })
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or does not belong to user"
            )
        
        chat_session = ChatSession(**session)
        
        # Check if this is the first message (for title generation)
        is_first_message = len(chat_session.messages) == 0
        
        # Process audio if provided (voice-to-text)
        user_message_text = message
        if audio:
            try:
                audio_bytes = await audio.read()
                transcribed_text = await openai_service.transcribe_audio(
                    audio_bytes,
                    filename=audio.filename or "recording.webm"
                )
                
                # Combine or use transcribed text
                if user_message_text:
                    user_message_text = f"{user_message_text} {transcribed_text}"
                else:
                    user_message_text = transcribed_text
                    
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Audio transcription failed: {str(e)}"
                )
        
        # Validate that we have some input
        if not user_message_text and not image:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one of message, audio, or image must be provided"
            )
        
        # Process image if provided
        image_data = None
        if image:
            try:
                image_bytes = await image.read()
                # Convert to base64
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                # Determine image type
                content_type = image.content_type or "image/jpeg"
                image_data = f"data:{content_type};base64,{image_base64}"
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image processing failed: {str(e)}"
                )
        
        # Generate title from first message (if this is the first message)
        if is_first_message and user_message_text:
            try:
                generated_title = await openai_service.generate_title(user_message_text)
                chat_session.title = generated_title
            except Exception as e:
                # If title generation fails, use fallback
                chat_session.title = user_message_text[:40].strip() + ("..." if len(user_message_text) > 40 else "")
        
        # Prepare user message content
        if image_data:
            # Multi-modal message with image
            user_content = []
            if user_message_text:
                user_content.append(MessageContent(type="text", text=user_message_text))
            user_content.append(MessageContent(
                type="image_url",
                image_url=validate_image_url(image_data)
            ))
        else:
            # Text-only message
            user_content = user_message_text
        
        # Create user message
        user_message = Message(
            role="user",
            content=user_content,
            timestamp=datetime.utcnow()
        )
        
        # Add user message to session
        chat_session.messages.append(user_message)
        
        # Prepare messages for OpenAI API
        openai_messages = []
        for msg in chat_session.messages:
            if isinstance(msg.content, str):
                openai_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            else:
                # Multi-modal content
                content_list = []
                for content_item in msg.content:
                    if content_item.type == "text":
                        content_list.append({
                            "type": "text",
                            "text": content_item.text
                        })
                    elif content_item.type == "image_url":
                        content_list.append({
                            "type": "image_url",
                            "image_url": content_item.image_url
                        })
                
                openai_messages.append({
                    "role": msg.role,
                    "content": content_list
                })
        
        # Get AI response
        try:
            ai_response = await openai_service.chat_completion(openai_messages)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"OpenAI API error: {str(e)}"
            )
        
        # Create assistant message
        assistant_message = Message(
            role="assistant",
            content=ai_response,
            timestamp=datetime.utcnow()
        )
        
        # Add assistant message to session
        chat_session.messages.append(assistant_message)
        chat_session.updated_at = datetime.utcnow()
        
        # Save to MongoDB (including updated title if first message)
        await collection.update_one(
            {"session_id": session_id, "user_id": user_id},
            {"$set": chat_session.model_dump()},
            upsert=True
        )
        
        return ChatResponse(
            session_id=session_id,
            title=chat_session.title,  # Return current title
            message=ai_response,
            timestamp=assistant_message.timestamp
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@chat_router.get("/history/{session_id}", response_model=SessionHistoryResponse, status_code=status.HTTP_200_OK)
async def get_session_history(
    session_id: str,
    user_id: str
):
    """
    Get chat history for a specific session
    
    **Step 3:** View conversation history
    
    **Parameters:**
    - session_id: The session ID (path parameter)
    - user_id: Your user ID (query parameter)
    
    **Returns:** All messages in this session with the session title
    """
    try:
        collection = database.get_collection()
        
        # Find session
        session = await collection.find_one({
            "session_id": session_id,
            "user_id": user_id
        })
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or does not belong to user"
            )
        
        chat_session = ChatSession(**session)
        
        return SessionHistoryResponse(
            session_id=chat_session.session_id,
            user_id=chat_session.user_id,
            title=chat_session.title,  # Include title in response
            messages=chat_session.messages,
            created_at=chat_session.created_at,
            updated_at=chat_session.updated_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session history: {str(e)}"
        )


@chat_router.delete("/session/{session_id}", status_code=status.HTTP_200_OK)
async def delete_session(
    session_id: str,
    user_id: str
):
    """
    Delete a specific chat session
    
    **Step 4:** Delete conversation
    
    **Parameters:**
    - session_id: The session to delete (path parameter)
    - user_id: Your user ID (query parameter)
    
    **Security:** Only the session owner can delete it
    """
    try:
        collection = database.get_collection()
        
        # Delete session (only if belongs to user)
        result = await collection.delete_one({
            "session_id": session_id,
            "user_id": user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or does not belong to user"
            )
        
        return {
            "message": "Session deleted successfully",
            "session_id": session_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )


@chat_router.get("/sessions/list", status_code=status.HTTP_200_OK)
async def list_user_sessions(user_id: str):
    """
    List all sessions for a user
    
    **Bonus Endpoint:** See all your conversations with titles
    
    **Parameters:**
    - user_id: Your user ID (query parameter)
    
    **Returns:** List of all sessions with title, message count, and timestamps
    """
    try:
        collection = database.get_collection()
        
        # Find all sessions for user
        cursor = collection.find(
            {"user_id": user_id},
            {"session_id": 1, "title": 1, "created_at": 1, "updated_at": 1, "messages": 1, "_id": 0}
        ).sort("updated_at", -1)
        
        sessions = await cursor.to_list(length=None)
        
        # Add message count and title to each session
        session_list = []
        for session in sessions:
            session_list.append({
                "session_id": session["session_id"],
                "title": session.get("title", "New Chat"),  # Include title
                "message_count": len(session.get("messages", [])),
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
            detail=f"Failed to list sessions: {str(e)}"
        )
