import asyncio
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from schemas import ExtractionResult, InputType
from utils.text import clean_text, extract_video_id


async def extract_youtube(url: str) -> ExtractionResult:
    try:
        video_id = extract_video_id(url)
        if not video_id:
            return ExtractionResult(
                input_type=InputType.YOUTUBE,
                extracted_text="",
                error="Invalid YouTube URL"
            )
        
        def _fetch():
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join(entry['text'] for entry in transcript)
        
        text = await asyncio.to_thread(_fetch)
        return ExtractionResult(
            input_type=InputType.YOUTUBE,
            extracted_text=clean_text(text),
            metadata={"video_id": video_id}
        )
    except (TranscriptsDisabled, NoTranscriptFound):
        return ExtractionResult(
            input_type=InputType.YOUTUBE,
            extracted_text="",
            error="No transcript available"
        )
    except Exception as e:
        return ExtractionResult(
            input_type=InputType.YOUTUBE,
            extracted_text="",
            error=str(e)
        )
