import asyncio
from io import BytesIO

from PyPDF2 import PdfReader

from infrastructure.logging import get_logger
from schemas import ExtractionResult, InputType
from utils.text import clean_text
from .base import ExtractorRegistry


logger = get_logger("extractor.pdf")


@ExtractorRegistry.register("pdf", ["pdf"])
async def extract_pdf(content: bytes, filename: str | None = None) -> ExtractionResult:
    def _parse():
        reader = PdfReader(BytesIO(content))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text, len(reader.pages)

    try:
        text, pages = await asyncio.to_thread(_parse)
        logger.info("pdf_extracted", pages=pages, chars=len(text))
        return ExtractionResult(
            input_type=InputType.PDF,
            extracted_text=clean_text(text),
            metadata={"pages": pages}
        )
    except Exception as e:
        logger.error("pdf_extraction_failed", error=str(e), exc_info=True)
        return ExtractionResult(
            input_type=InputType.PDF,
            extracted_text="",
            error=str(e)
        )

