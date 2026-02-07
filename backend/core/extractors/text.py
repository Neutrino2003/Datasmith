from schemas import ExtractionResult, InputType
from utils.text import clean_text


async def extract_text(content: str | bytes) -> ExtractionResult:
    if isinstance(content, bytes):
        content = content.decode('utf-8', errors='ignore')
    
    return ExtractionResult(
        input_type=InputType.TEXT,
        extracted_text=clean_text(content)
    )
