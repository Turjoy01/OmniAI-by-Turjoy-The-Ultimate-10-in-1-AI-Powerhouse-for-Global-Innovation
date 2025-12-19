from fastapi import APIRouter, UploadFile, File, HTTPException, status
from services.openai_service import OpenAIService

voice_router = APIRouter(prefix="/api/voice", tags=["Voice"])
openai_service = OpenAIService()

@voice_router.post("/transcribe", status_code=status.HTTP_200_OK)
async def transcribe_voice(
    audio: UploadFile = File(..., description="Audio file to transcribe")
):
    """
    Transcribe voice to text
    
    **Simple Voice-to-Text:**
    - Upload an audio file
    - Receives transcribed text in response
    """
    try:
        audio_bytes = await audio.read()
        transcribed_text = await openai_service.transcribe_audio(
            audio_bytes,
            filename=audio.filename or "recording.webm"
        )
        
        return {
            "text": transcribed_text,
            "filename": audio.filename,
            "success": True
        }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )
