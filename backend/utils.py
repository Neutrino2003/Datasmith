import re
import mimetypes
from pathlib import Path
from typing import Optional


def detect_youtube_url(text: str) -> Optional[str]:
    """Detect YouTube URL in text."""
    patterns = [
        r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(https?://)?(www\.)?youtu\.be/[\w-]+',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def extract_video_id(youtube_url: str) -> Optional[str]:
    """Extract video ID from YouTube URL."""
    match = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([^&\n?#]+)', youtube_url)
    return match.group(1) if match else None


def get_file_type(filename: str) -> str:
    """Determine file type from filename."""
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type:
        if mime_type.startswith('image/'):
            return 'image'
        elif mime_type == 'application/pdf':
            return 'pdf'
        elif mime_type.startswith('audio/'):
            return 'audio'
    ext = Path(filename).suffix.lower()
    if ext in {'.jpg', '.jpeg', '.png', '.gif', '.webp'}:
        return 'image'
    elif ext == '.pdf':
        return 'pdf'
    elif ext in {'.mp3', '.wav', '.m4a', '.ogg', '.flac'}:
        return 'audio'
    return 'unknown'


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()


def is_code_content(text: str) -> bool:
    """Detect if text contains code."""
    patterns = [
        r'\bdef\s+\w+\s*\(', r'\bfunction\s+\w+\s*\(', r'\bclass\s+\w+',
        r'\bimport\s+', r'\breturn\s+', r'\bif\s*\(.+\)\s*{',
    ]
    return any(re.search(p, text, re.MULTILINE) for p in patterns)
