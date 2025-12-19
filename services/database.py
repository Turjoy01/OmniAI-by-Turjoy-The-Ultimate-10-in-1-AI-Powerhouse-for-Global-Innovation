from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class Database:
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB"""
        cls.client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
        print("✅ Connected to MongoDB Atlas")
    
    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            print("❌ MongoDB connection closed")
    
    @classmethod
    def get_database(cls):
        """Get database instance"""
        return cls.client[os.getenv("DATABASE_NAME", "chatgpt_clone")]
    
    @classmethod
    def get_collection(cls):
        """Get collection instance (default: chat_sessions)"""
        db = cls.get_database()
        return db[os.getenv("COLLECTION_NAME", "chat_sessions")]
    
    @classmethod
    def get_collection_by_name(cls, collection_name: str):
        """
        Get collection instance by name
        
        Args:
            collection_name: Name of the collection (e.g., 'business_sessions', 'social_sessions', 'agents_sessions')
        
        Returns:
            Collection instance
        """
        db = cls.get_database()
        return db[collection_name]


database = Database()