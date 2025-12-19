"""
Unified Routes Package

Contains all API routes for Business, Social Media, AI Agents, and Chat tools.
"""

from fastapi import APIRouter
from .business_routes import business_router
from .social_routes import social_router
from .agents_routes import agents_router
from .chat_routes import chat_router
from .voice_routes import voice_router

# Create main router
main_router = APIRouter()

# Include all sub-routers
main_router.include_router(business_router)
main_router.include_router(social_router)
main_router.include_router(agents_router)
main_router.include_router(chat_router)
main_router.include_router(voice_router)

__all__ = ["main_router", "business_router", "social_router", "agents_router", "chat_router", "voice_router"]
