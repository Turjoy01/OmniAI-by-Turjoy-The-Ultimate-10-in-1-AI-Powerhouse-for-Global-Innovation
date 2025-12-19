from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from typing import Optional, Union, Dict, List
from datetime import datetime
import uuid
import base64

from models.responses import (
    SessionCreateResponse,
    ChatResponse, 
    ChatSession, 
    Message,
    MessageContent
)
from services.openai_service import OpenAIService
from utils.audio_processing import validate_image_url

temp_chat_router = APIRouter(prefix="/api/temp-chat", tags=["Temporary Chat"])
openai_service = OpenAIService()

# In-memory storage for temporary sessions
# Structure: {session_id: ChatSession}
TEMP_SESSIONS: Dict[str, ChatSession] = {}

@temp_chat_router.post("/session/create", response_model=SessionCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_temp_session(user_id: str = Form(..., description="User ID")):
    """
    Create a new TEMPORARY chat session
    
    **Note:** This session is NOT saved to the database. It exists only in memory.
    """
    try:
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Create new session with default title
        chat_session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            title="Temporary Chat",
            messages=[]
        )
        
        # Save to In-Memory Storage
        TEMP_SESSIONS[session_id] = chat_session
        
        return SessionCreateResponse(
            session_id=session_id,
            user_id=user_id,
            title=chat_session.title,
            message="Temporary session created successfully",
            created_at=chat_session.created_at
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@temp_chat_router.post("/message", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def send_temp_message(
    user_id: str = Form(..., description="User ID"),
    session_id: str = Form(..., description="Session ID from /session/create"),
    message: str = Form("", description="Text message (optional if audio/image provided)"),
    audio: Union[UploadFile, str, None] = File(None, description="Audio file - auto converts to text"),
    image: Union[UploadFile, str, None] = File(None, description="Image file upload")
):
    """
    Send a message to a TEMPORARY session
    """
    try:
        # Normalize inputs
        if isinstance(audio, str):
            audio = None
        if isinstance(image, str):
            image = None

        # Verify session exists in memory
        if session_id not in TEMP_SESSIONS:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Temporary session not found (it may have been cleared on server restart)"
            )
        
        chat_session = TEMP_SESSIONS[session_id]
        
        # Verify user owns this session
        if chat_session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Session does not belong to user"
            )
        
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
                
                if user_message_text:
                    user_message_text = f"{user_message_text} {transcribed_text}"
                else:
                    user_message_text = transcribed_text
                    
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Audio transcription failed: {str(e)}"
                )
        
        # Validate input
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
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                content_type = image.content_type or "image/jpeg"
                image_data = f"data:{content_type};base64,{image_base64}"
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image processing failed: {str(e)}"
                )
        
        # Generate title from first message
        if is_first_message and user_message_text:
            try:
                generated_title = await openai_service.generate_title(user_message_text)
                chat_session.title = generated_title
            except Exception:
                chat_session.title = user_message_text[:40].strip() + ("..." if len(user_message_text) > 40 else "")
        
        # Prepare user message content
        if image_data:
            user_content = []
            if user_message_text:
                user_content.append(MessageContent(type="text", text=user_message_text))
            user_content.append(MessageContent(
                type="image_url",
                image_url=validate_image_url(image_data)
            ))
        else:
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
        
        # No DB update needed - it's already updated in the object reference in TEMP_SESSIONS
        
        return ChatResponse(
            session_id=session_id,
            title=chat_session.title,
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
