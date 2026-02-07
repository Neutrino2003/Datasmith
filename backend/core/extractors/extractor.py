from schemas import ExtractionResult, InputType
from utils.text import detect_youtube_url, get_file_type
from .base import ExtractorRegistry

from . import pdf, image, audio, text


async def extract_content(
    content: bytes | str,
    filename: str | None = None
) -> ExtractionResult:
    if isinstance(content, str):
        if detect_youtube_url(content):
            from .youtube import extract_youtube
            return await extract_youtube(content)
        return await text.extract_text(content)

    if not filename:
        return await text.extract_text(content)

    extractor = ExtractorRegistry.get_extractor(filename)
    if extractor:
        return await extractor(content, filename)

    return await text.extract_text(content)
