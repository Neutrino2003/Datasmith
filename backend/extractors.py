"""
Content Extractors for Datasmith AI
Handles PDF, Audio, Image, and YouTube extraction.
"""

import io
import asyncio
from pathlib import Path
from typing import Optional

from PIL import Image
from PyPDF2 import PdfReader
from deepgram import DeepgramClient
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from google import genai


from config import get_settings
from schemas import ExtractionResult, InputType
from utils import detect_youtube_url, extract_video_id, get_file_type, clean_text


class ContentExtractor:
    """Extracts text from different input types."""
    
    def __init__(self):
        self.settings = get_settings()
        self._deepgram = None
    
    @property
    def deepgram(self):
        if self._deepgram is None:
            self._deepgram = DeepgramClient(api_key=self.settings.deepgram_api_key)
        return self._deepgram
    
    async def extract(self, content, filename: Optional[str] = None) -> ExtractionResult:
        try:
            if isinstance(content, str):
                if detect_youtube_url(content):
                    return await self._youtube(content)
                return ExtractionResult(input_type=InputType.TEXT, extracted_text=clean_text(content))
            
            if filename:
                file_type = get_file_type(filename)
                if file_type == "pdf":
                    return await self._pdf(content)
                elif file_type == "image":
                    return await self._image(content)
                elif file_type == "audio":
                    return await self._audio(content, filename)
                elif file_type == "text":
                    return ExtractionResult(input_type=InputType.TEXT, extracted_text=content.decode('utf-8', errors='ignore'))
            
            return ExtractionResult(input_type=InputType.TEXT, extracted_text=content.decode('utf-8', errors='ignore'))
        except Exception as e:
            return ExtractionResult(input_type=InputType.TEXT, extracted_text="", error=str(e))
    
    async def _image(self, content: bytes) -> ExtractionResult:
        try:
            client = genai.Client(api_key=self.settings.google_api_key)
            
            image = Image.open(io.BytesIO(content))
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='JPEG')
            img_bytes = img_buffer.getvalue()
            
            response = await asyncio.to_thread(
                lambda: client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=["Extract all text from this image. If no text, describe what you see.", {"mime_type": "image/jpeg", "data": img_bytes}]
                )
            )
            return ExtractionResult(input_type=InputType.IMAGE, extracted_text=clean_text(response.text or ""))
        except Exception as e:
            return ExtractionResult(input_type=InputType.IMAGE, extracted_text="", error=str(e))
    
    async def _pdf(self, content: bytes) -> ExtractionResult:
        def parse():
            reader = PdfReader(io.BytesIO(content))
            return "\n".join(page.extract_text() or "" for page in reader.pages), len(reader.pages)
        
        text, pages = await asyncio.to_thread(parse)
        return ExtractionResult(input_type=InputType.PDF, extracted_text=clean_text(text), metadata={"pages": pages})
    
    async def _audio(self, content: bytes, filename: str) -> ExtractionResult:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.deepgram.com/v1/listen",
                    headers={"Authorization": f"Token {self.settings.deepgram_api_key}", "Content-Type": "audio/wav"},
                    params={"model": "nova-2", "smart_format": "true"},
                    content=content
                )
                if response.status_code == 200:
                    data = response.json()
                    transcript = data.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
                    return ExtractionResult(input_type=InputType.AUDIO, extracted_text=clean_text(transcript))
                return ExtractionResult(input_type=InputType.AUDIO, extracted_text="", error=f"Deepgram error: {response.status_code}")
        except Exception as e:
            return ExtractionResult(input_type=InputType.AUDIO, extracted_text="", error=str(e))
    
    async def _youtube(self, url: str) -> ExtractionResult:
        try:
            video_id = extract_video_id(url)
            if not video_id:
                return ExtractionResult(input_type=InputType.YOUTUBE, extracted_text="", error="Invalid YouTube URL")
            
            def fetch():
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                return " ".join(entry['text'] for entry in transcript)
            
            text = await asyncio.to_thread(fetch)
            return ExtractionResult(input_type=InputType.YOUTUBE, extracted_text=clean_text(text), metadata={"video_id": video_id})
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            return ExtractionResult(input_type=InputType.YOUTUBE, extracted_text="", error="No transcript available")
        except Exception as e:
            return ExtractionResult(input_type=InputType.YOUTUBE, extracted_text="", error=str(e))
