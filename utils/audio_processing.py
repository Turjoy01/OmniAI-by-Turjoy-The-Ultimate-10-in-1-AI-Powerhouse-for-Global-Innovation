"""
Audio Processing Utilities

Helper functions for audio and image processing in chat features.
"""

import base64
from io import BytesIO


def decode_base64_audio(audio_base64: str) -> bytes:
    """
    Decode base64 encoded audio to bytes
    
    Args:
        audio_base64: Base64 encoded audio string
    
    Returns:
        Audio bytes
    """
    # Remove data URI prefix if present
    if "," in audio_base64:
        audio_base64 = audio_base64.split(",")[1]
    
    return base64.b64decode(audio_base64)


def validate_image_url(image_input: str) -> dict:
    """
    Validate and format image input for OpenAI API
    
    Args:
        image_input: Base64 string or URL
    
    Returns:
        Formatted image_url dict
    """
    if image_input.startswith("http://") or image_input.startswith("https://"):
        return {"url": image_input}
    else:
        # It's a base64 encoded image
        if not image_input.startswith("data:"):
            # Add data URI prefix
            image_input = f"data:image/jpeg;base64,{image_input}"
        return {"url": image_input}

