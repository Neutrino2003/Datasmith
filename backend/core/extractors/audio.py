import httpx

from infrastructure.config import get_settings
from infrastructure.logging import get_logger
from schemas import ExtractionResult, InputType
from utils.text import clean_text
from .base import ExtractorRegistry


logger = get_logger("extractor.audio")


@ExtractorRegistry.register("audio", ["wav", "mp3", "m4a", "ogg", "flac"])
async def extract_audio(content: bytes, filename: str | None = None) -> ExtractionResult:
    try:
        settings = get_settings()

        async with httpx.AsyncClient(timeout=settings.deepgram_timeout_sec) as client:
            response = await client.post(
                "https://api.deepgram.com/v1/listen",
                headers={
                    "Authorization": f"Token {settings.deepgram_api_key}",
                    "Content-Type": "audio/wav"
                },
                params={"model": "nova-2", "smart_format": "true"},
                content=content
            )

            if response.status_code == 200:
                data = response.json()
                transcript = (
                    data.get("results", {})
                    .get("channels", [{}])[0]
                    .get("alternatives", [{}])[0]
                    .get("transcript", "")
                )
                logger.info("audio_extracted", chars=len(transcript))
                return ExtractionResult(
                    input_type=InputType.AUDIO,
                    extracted_text=clean_text(transcript)
                )

            logger.error("deepgram_error", status_code=response.status_code)
            return ExtractionResult(
                input_type=InputType.AUDIO,
                extracted_text="",
                error=f"Deepgram error: {response.status_code}"
            )
    except Exception as e:
        logger.error("audio_extraction_failed", error=str(e), exc_info=True)
        return ExtractionResult(
            input_type=InputType.AUDIO,
            extracted_text="",
            error=str(e)
        )

