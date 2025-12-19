from fastapi import APIRouter, HTTPException, status
from typing import List

from models.student_tools import (
    CreateSessionRequest, SessionResponse, HistoryResponse,
    HomeworkRequest, EssayRequest, MathRequest, StudyRequest,
    FlashcardsRequest, SummaryRequest, StudentToolResponse
)
from services.student_service import StudentService

# Initialize router
student_router = APIRouter(prefix="/api/student", tags=["AI for Students"])

# Initialize service
service = StudentService()

@student_router.post("/session/create", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(request: CreateSessionRequest):
    """Create a new Student Tools session"""
    try:
        session_id = await service.create_session(user_id=request.user_id)
        return SessionResponse(
            session_id=session_id,
            user_id=request.user_id,
            message="Student session created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@student_router.post("/homework", response_model=StudentToolResponse)
async def homework_helper(request: HomeworkRequest):
    """Homework Helper tool"""
    try:
        return await service.homework_helper(**request.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@student_router.post("/essay", response_model=StudentToolResponse)
async def essay_generator(request: EssayRequest):
    """Essay Generator tool"""
    try:
        return await service.essay_generator(**request.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@student_router.post("/math", response_model=StudentToolResponse)
async def math_solver(request: MathRequest):
    """Math Solver with steps tool"""
    try:
        return await service.math_solver(**request.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@student_router.post("/study", response_model=StudentToolResponse)
async def study_mode(request: StudyRequest):
    """Study Mode (Interactive Session) tool"""
    try:
        return await service.study_mode(**request.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@student_router.post("/flashcards", response_model=StudentToolResponse)
async def generate_flashcards(request: FlashcardsRequest):
    """Flashcards Generation tool"""
    try:
        return await service.generate_flashcards(**request.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@student_router.post("/summary", response_model=StudentToolResponse)
async def summarize_text(request: SummaryRequest):
    """Summarization tool"""
    try:
        return await service.summarize_text(**request.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@student_router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(session_id: str):
    """Get student tool interaction history"""
    try:
        interactions = await service.get_history(session_id)
        return HistoryResponse(
            session_id=session_id,
            interactions=interactions
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@student_router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a student tools session"""
    try:
        await service.delete_session(session_id)
        return {"message": "Session deleted successfully", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
