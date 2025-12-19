from datetime import datetime
import uuid
from typing import List, Optional
from fastapi import HTTPException, status

from models.group_chat import Group, GroupMessage, GroupType, GroupChatSession
from services.database import database
from services.openai_service import OpenAIService

class GroupChatService:
    def __init__(self):
        self.openai_service = OpenAIService()

    async def create_session(self, user_id: str) -> str:
        """
        Create a new group chat session for the user.
        Returns the session_id.
        """
        collection = database.get_collection_by_name("group_chat_sessions")
        
        session_id = str(uuid.uuid4())
        
        session = GroupChatSession(
            session_id=session_id,
            user_id=user_id,
        )
        
        await collection.insert_one(session.model_dump())
        return session_id

    async def _validate_session(self, session_id: str, user_id: str):
        """
        Verify that the session exists and belongs to the user.
        """
        collection = database.get_collection_by_name("group_chat_sessions")
        session = await collection.find_one({
            "session_id": session_id,
            "user_id": user_id
        })
        if not session:
            raise HTTPException(status_code=401, detail="Invalid session or user mismatch")

    async def create_group(self, user_id: str, session_id: str, name: str, group_type: GroupType) -> Group:
        # Validate Session
        await self._validate_session(session_id, user_id)

        collection = database.get_collection_by_name("groups")
        
        group_id = str(uuid.uuid4())
        
        group = Group(
            group_id=group_id,
            name=name,
            type=group_type,
            creator_id=user_id,
            members=[user_id]
        )
        
        await collection.insert_one(group.model_dump())
        return group

    async def join_group(self, user_id: str, session_id: str, group_id: str) -> Group:
        # Validate Session
        await self._validate_session(session_id, user_id)

        collection = database.get_collection_by_name("groups")
        
        group_data = await collection.find_one({"group_id": group_id})
        if not group_data:
            raise HTTPException(status_code=404, detail="Group not found")
        
        group = Group(**group_data)
        
        if user_id not in group.members:
            group.members.append(user_id)
            await collection.update_one(
                {"group_id": group_id},
                {"$set": {"members": group.members}}
            )
            
        return group

    async def send_message(self, group_id: str, session_id: str, user_id: str, content: str) -> GroupMessage:
        # Validate Session
        await self._validate_session(session_id, user_id)

        collection = database.get_collection_by_name("groups")
        
        group_data = await collection.find_one({"group_id": group_id})
        if not group_data:
            raise HTTPException(status_code=404, detail="Group not found")
        
        group = Group(**group_data)
        
        if user_id not in group.members:
            raise HTTPException(status_code=403, detail="User is not a member of this group")

        # 1. Save User Message
        user_message_id = str(uuid.uuid4())
        user_message = GroupMessage(
            message_id=user_message_id,
            user_id=user_id,
            content=content,
            timestamp=datetime.utcnow(),
            is_ai=False
        )
        
        # Update group with user message
        new_messages = group.messages + [user_message]
        await collection.update_one(
            {"group_id": group_id},
            {"$push": {"messages": user_message.model_dump()}}
        )

        # 2. Generate AI Response
        # Construct context from previous messages
        context_messages = [
            {"role": "system", "content": f"You are a helpful assistant in a {group.type.value} group chat. Answer the user's question mostly for {group.type.value} context."}
        ]
        
        # Add last 10 messages for context
        for msg in new_messages[-10:]:
            role = "assistant" if msg.is_ai else "user"
            context_messages.append({"role": role, "content": msg.content})

        try:
            ai_response_content = await self.openai_service.chat_completion(
                messages=context_messages,
                temperature=0.7,
                max_tokens=500
            )
        except Exception as e:
            # Fallback or error logging
            print(f"Error generating AI response: {e}")
            ai_response_content = "I'm having trouble connecting right now. Please try again later."

        # 3. Save AI Response
        ai_message_id = str(uuid.uuid4())
        ai_message = GroupMessage(
            message_id=ai_message_id,
            user_id="AI",
            content=ai_response_content,
            timestamp=datetime.utcnow(),
            is_ai=True
        )
        
        await collection.update_one(
            {"group_id": group_id},
            {"$push": {"messages": ai_message.model_dump()}}
        )

        return ai_message

    async def get_group_history(self, group_id: str) -> List[GroupMessage]:
        collection = database.get_collection_by_name("groups")
        
        group_data = await collection.find_one({"group_id": group_id})
        if not group_data:
            raise HTTPException(status_code=404, detail="Group not found")
            
        group = Group(**group_data)
        return group.messages

    async def delete_group(self, group_id: str, user_id: str):
        collection = database.get_collection_by_name("groups")
        
        group_data = await collection.find_one({"group_id": group_id})
        if not group_data:
            raise HTTPException(status_code=404, detail="Group not found")
        
        if group_data["creator_id"] != user_id:
            raise HTTPException(status_code=403, detail="Only the creator can delete the group")
            
        await collection.delete_one({"group_id": group_id})
