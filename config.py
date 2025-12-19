"""
Application Configuration

Unified configuration for the entire application.
Uses environment variables with sensible defaults.
"""

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Global application configuration.
    All settings can be overridden via environment variables or .env file.
    """
    
    APP_NAME: str = "OmniAI by Turjoy"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "OmniAI by Turjoy: The Ultimate 10-in-1 AI Powerhouse for Global Innovation"
    
    # Server Configuration
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = ""  
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_MAX_TOKENS: int = 2048
    OPENAI_TEMPERATURE: float = 0.7
    
    # ElevenLabs Configuration
    ELEVENLABS_API_KEY: str = ""
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = ["*"]
    
    # MongoDB Configuration
    MONGODB_URI: str = ""
    DATABASE_NAME: str = "chatgpt_clone"
    COLLECTION_NAME: str = "chat_sessions"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Return a cached instance of settings.
    This ensures we don't re-read the environment variables repeatedly.
    """
    return Settings()

