"""
Unified OpenAI Service

Single service class for all OpenAI API interactions.
Used by both Business and Social Media services.
"""

from openai import OpenAI, AsyncOpenAI
from typing import Optional, List, Dict
from config import get_settings


class OpenAIService:
    """
    Unified OpenAI service for all AI-powered features.
    Provides methods for content generation with configurable parameters.
    """
    
    def __init__(self):
        """Initialize the OpenAI service with settings"""
        self.settings = get_settings()
        self.client = None
        self.async_client = None
        self._initialized = False
        self._async_initialized = False
    
    def _ensure_initialized(self):
        """Lazy initialization - only create client when needed"""
        if not self._initialized:
            if not self.settings.OPENAI_API_KEY:
                raise ValueError(
                    "OPENAI_API_KEY is not set. Please set it in your .env file or environment variables.\n"
                    "Get your API key from: https://platform.openai.com/api-keys"
                )
            self.client = OpenAI(api_key=self.settings.OPENAI_API_KEY)
            self._initialized = True
    
    def _ensure_async_initialized(self):
        """Lazy initialization for async client"""
        if not self._async_initialized:
            if not self.settings.OPENAI_API_KEY:
                raise ValueError(
                    "OPENAI_API_KEY is not set. Please set it in your .env file or environment variables.\n"
                    "Get your API key from: https://platform.openai.com/api-keys"
                )
            self.async_client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
            self._async_initialized = True
    
    async def generate_completion(
        self,
        prompt: str,
        model: str = None,
        max_tokens: int = None,
        temperature: float = None,
        system_message: str = None
    ) -> str:
        """
        Generate content using OpenAI API
        
        Args:
            prompt: The prompt to send to the AI
            model: Model to use (defaults to settings)
            max_tokens: Maximum tokens in response (defaults to settings)
            temperature: Controls randomness 0.0-1.0 (defaults to settings)
            system_message: Custom system message (optional)
            
        Returns:
            Generated text content
            
        Raises:
            Exception: If API call fails
        """
        self._ensure_initialized()
        
        try:
            response = self.client.chat.completions.create(
                model=model or self.settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": system_message or "You are a helpful AI assistant."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens or self.settings.OPENAI_MAX_TOKENS,
                temperature=temperature or self.settings.OPENAI_TEMPERATURE,
            )
            
            if not response.choices or not response.choices[0].message.content:
                raise Exception("Empty response from OpenAI API")
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"OpenAI API Error: {str(e)}")
    
    def validate_api_key(self) -> bool:
        """
        Validate that the API key is working
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            self._ensure_initialized()
            # Try a simple generation to test the API key
            self.client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        except Exception:
            return False
    
    async def chat_completion(
        self, 
        messages: List[Dict], 
        temperature: float = 0.7,
        max_tokens: int = 2000,
        model: str = None
    ) -> str:
        """
        Get chat completion from OpenAI (async)
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            model: Model to use (defaults to gpt-4o for chat)
        
        Returns:
            Assistant's response text
        """
        self._ensure_async_initialized()
        
        try:
            response = await self.async_client.chat.completions.create(
                model=model or "gpt-4o",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API Error: {str(e)}")
    
    async def generate_title(self, first_message: str) -> str:
        """
        Generate a short, descriptive title from the first message
        
        Args:
            first_message: The user's first message in the conversation
        
        Returns:
            A short title (2-6 words)
        """
        self._ensure_async_initialized()
        
        try:
            # If message is too short, use it as title
            if len(first_message) <= 40:
                return first_message.strip()
            
            # Use GPT to generate a concise title
            prompt = f"""Generate a very short, descriptive title (2-6 words maximum) for a chat conversation that starts with this message:

"{first_message}"

Rules:
- Maximum 6 words
- No punctuation at the end
- Capture the main topic or intent
- Make it conversational and natural

Title:"""

            response = await self.async_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates short, descriptive titles for conversations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=20
            )
            
            title = response.choices[0].message.content.strip()
            
            # Clean up title (remove quotes if present)
            title = title.strip('"').strip("'").strip()
            
            # Limit to 50 characters max
            if len(title) > 50:
                title = title[:47] + "..."
            
            return title
        
        except Exception as e:
            # Fallback: use first 40 characters of message
            return first_message[:40].strip() + ("..." if len(first_message) > 40 else "")
    
    async def transcribe_audio(self, audio_data: bytes, filename: str = "audio.wav") -> str:
        """
        Transcribe audio to text using Whisper API
        
        Args:
            audio_data: Audio file bytes
            filename: Filename for the audio
        
        Returns:
            Transcribed text
        """
        self._ensure_async_initialized()
        
        try:
            # Create a file-like object from bytes
            from io import BytesIO
            audio_file = BytesIO(audio_data)
            audio_file.name = filename
            
            transcript = await self.async_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            return transcript.text
        except Exception as e:
            raise Exception(f"Audio Transcription Error: {str(e)}")

    async def generate_audio(self, text: str, voice: str = "alloy") -> bytes:
        """
        Generate audio from text using OpenAI TTS
        
        Args:
            text: Text to convert to speech
            voice: Voice ID (alloy, echo, fable, onyx, nova, shimmer)
            
        Returns:
            Audio bytes
        """
        self._ensure_async_initialized()
        
        try:
            response = await self.async_client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            return response.content
        except Exception as e:
            raise Exception(f"TTS Error: {str(e)}")
