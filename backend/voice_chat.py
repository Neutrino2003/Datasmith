import asyncio
import httpx
from config import get_settings


class VoiceChat:
    """Handle voice input using Deepgram REST API directly."""
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.deepgram_api_key
        self.base_url = "https://api.deepgram.com/v1/listen"
    
    async def transcribe(self, audio_bytes: bytes, mime_type: str = "audio/wav") -> str:
        """Convert speech to text using Deepgram REST API."""
        
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": mime_type
        }
        
        params = {
            "model": "nova-2",
            "smart_format": "true"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    params=params,
                    content=audio_bytes
                )
                
                if response.status_code != 200:
                    return f"[Deepgram error: {response.status_code}]"
                
                data = response.json()
                transcript = data.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
                
                return transcript if transcript else "[No speech detected]"
                
        except Exception as e:
            return f"[Transcription error: {e}]"
