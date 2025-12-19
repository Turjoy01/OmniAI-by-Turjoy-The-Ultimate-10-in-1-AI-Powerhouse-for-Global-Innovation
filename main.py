"""
OmniAI by Turjoy: The Ultimate 10-in-1 AI Powerhouse for Global Innovation
OmniAI by Turjoy is the pinnacle of AI convergence, blending multiple advanced AI technologies into a single, high-performance digital ecosystem. Powered by GPT-4o, Whisper-1, and TTS-1, OmniAI offers a transformative suite of tools for enterprises, content creators, students, and industries, propelling them into the future of intelligent automation, social media mastery, academic excellence, and real-time multilingual communication.
With an unwavering commitment to scalability, precision, and performance, OmniAI is built for the innovators, the creators, and the leaders who aim to revolutionize the digital landscape. Whether you're automating complex business operations, creating viral content, or empowering global communication, OmniAI is your ultimate AI ally.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from config import get_settings
from routes import main_router
from routes.temp_chat_routes import temp_chat_router
from routes.group_chat_routes import group_chat_router
from routes.global_language_routes import global_language_router
from routes.student_routes import student_router
from services.database import database

# Get settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    try:
        await database.connect_db()
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"⚠️  WARNING: MongoDB connection failed during startup")
        print(f"{'='*60}")
        print(f"Error: {str(e)}")
        print(f"\n⚠️  Chat features will not work without MongoDB connection")
        print(f"{'='*60}\n")
    yield
    # Shutdown
    try:
        await database.close_db()
    except Exception:
        pass

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include all routes
app.include_router(main_router)
app.include_router(temp_chat_router)
app.include_router(group_chat_router)
app.include_router(global_language_router)
app.include_router(student_router)




@app.get("/")
async def root():
    """
    API Root - Welcome endpoint with available features
    """
    return {
        "message": "OmniAI by Turjoy: The Ultimate 10-in-1 AI Powerhouse for Global Innovation",
        "version": settings.VERSION,
        "features": {
            "business_tools": {
                "ads_generator": "/api/business/ads/generate",
                "invoice_generator": "/api/business/invoice/generate",
                "email_generator": "/api/business/email/generate",
                "crm_tools": "/api/business/crm/process",
                "menu_generator": "/api/business/menu/generate",
                "seo_tools": "/api/business/seo/generate",
                "product_descriptions": "/api/business/product/description"
            },
            "social_media_tools": {
                "caption": "/api/social/caption",
                "hashtags": "/api/social/hashtags",
                "content_ideas": "/api/social/content-ideas",
                "video_title": "/api/social/video/title",
                "video_description": "/api/social/video/description",
                "video_tags": "/api/social/video/tags"
            },
            "ai_agents_marketplace": {
                "overview": "Choose AI agents tailored to marketing, restaurant, real estate, legal, teaching, or fitness use cases.",
                "suggestions_endpoint": "/api/agents/suggestions",
                "available_agents": [
                    "marketing",
                    "restaurant",
                    "real_estate",
                    "legal",
                    "teacher",
                    "fitness",
                    "business_plan_builder",
                    "financial_forecasts",
                    "industry_research",
                    "liveplan_assistant",
                ],
            },
            "chat": {
                "create_session": "POST /api/chat/session/create",
                "send_message": "POST /api/chat/message",
                "get_history": "GET /api/chat/history/{session_id}",
                "delete_session": "DELETE /api/chat/session/{session_id}",
                "list_sessions": "GET /api/chat/sessions/list",
            },
            "voice_tools": {
                "transcribe": "POST /api/voice/transcribe"
            },
            "group_chat": {
                "create_session": "POST /api/group-chat/session/create",
                "create_group": "POST /api/group-chat/group/create",
                "join_group": "POST /api/group-chat/group/join",
                "send_message": "POST /api/group-chat/group/message",
                "get_history": "GET /api/group-chat/group/history/{group_id}",
                "delete_group": "DELETE /api/group-chat/group/{group_id}"
            },
            "global_language": {
                "create_session": "POST /api/global-language/session/create",
                "voice_to_voice": "POST /api/global-language/voice (Multipart: audio_file, target_language)",
                "multilingual_chat": "POST /api/global-language/chat",
                "history": "GET /api/global-language/history/{session_id}",
                "delete_session": "DELETE /api/global-language/session/{session_id}"
            },
            "ai_for_students": {
                "create_session": "POST /api/student/session/create",
                "homework_helper": "POST /api/student/homework",
                "essay_generator": "POST /api/student/essay",
                "math_solver": "POST /api/student/math",
                "study_mode": "POST /api/student/study",
                "flashcards": "POST /api/student/flashcards",
                "summary": "POST /api/student/summary",
                "history": "GET /api/student/history/{session_id}",
                "delete_session": "DELETE /api/student/session/{session_id}"
            }
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
