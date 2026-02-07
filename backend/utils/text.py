import re
import mimetypes
from pathlib import Path


def detect_youtube_url(text: str) -> str | None:
    patterns = [
        r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(https?://)?(www\.)?youtu\.be/[\w-]+',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def extract_video_id(youtube_url: str) -> str | None:
    match = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([^&\n?#]+)', youtube_url)
    return match.group(1) if match else None


def get_file_type(filename: str) -> str:
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
    
    return 'text'


def clean_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()


def is_code_content(text: str) -> bool:
    patterns = [
        r'\bdef\s+\w+\s*\(',
        r'\bfunction\s+\w+\s*\(',
        r'\bclass\s+\w+',
        r'\bimport\s+',
        r'\breturn\s+',
        r'\bif\s*\(.+\)\s*{',
    ]
    return any(re.search(p, text, re.MULTILINE) for p in patterns)


def parse_llm_json(content: str | list | dict) -> dict | list:
    """Safely parse JSON from LLM response, handling Markdown code blocks and list content."""
    import json
    import ast
    
    if isinstance(content, list):
        # Join list parts if content is a list (common in multimodal responses)
        content = "".join(str(part) for part in content)
    elif not isinstance(content, str):
        content = str(content)
        
    content = content.replace("```json", "").replace("```", "").strip()
    
    # Try standard JSON parse
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Fallback 1: Try ast.literal_eval for Python-style dicts (single quotes)
    try:
        return ast.literal_eval(content)
    except (ValueError, SyntaxError):
        pass

    # Fallback 2: Try to find first { and last } and parse that
    try:
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = content[start:end]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                return ast.literal_eval(json_str)
    except:
        pass
        
    raise ValueError(f"Could not parse JSON content: {content[:100]}...")
