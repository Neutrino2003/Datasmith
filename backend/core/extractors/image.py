import asyncio
from io import BytesIO

from PIL import Image
from google import genai

from infrastructure.config import get_settings
from infrastructure.dependencies import get_genai_client
from infrastructure.logging import get_logger
from schemas import ExtractionResult, InputType
from utils.text import clean_text
from .base import ExtractorRegistry


logger = get_logger("extractor.image")


@ExtractorRegistry.register("image", ["jpg", "jpeg", "png", "gif", "webp", "bmp"])
async def extract_image(content: bytes, filename: str | None = None) -> ExtractionResult:
    try:
        settings = get_settings()
        client = get_genai_client()

        image = Image.open(BytesIO(content))
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        img_buffer = BytesIO()
        image.save(img_buffer, format="JPEG")
        img_bytes = img_buffer.getvalue()

        response = await asyncio.to_thread(
            lambda: client.models.generate_content(
                model=settings.llm_model,
                contents=[
                    "Extract all text from this image. If no text, describe what you see.",
                    {"mime_type": "image/jpeg", "data": img_bytes}
                ]
            )
        )

        text = response.text or ""
        logger.info("image_extracted", chars=len(text))
        return ExtractionResult(
            input_type=InputType.IMAGE,
            extracted_text=clean_text(text)
        )
    except Exception as e:
        logger.error("image_extraction_failed", error=str(e), exc_info=True)
        return ExtractionResult(
            input_type=InputType.IMAGE,
            extracted_text="",
            error=str(e)
        )

