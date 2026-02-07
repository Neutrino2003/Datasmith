from fastapi import APIRouter, HTTPException, UploadFile, File, Depends

from api.middleware.validation import validate_upload
from core.extractors.extractor import extract_content
from core.extractors.youtube import extract_youtube
from schemas import ExtractionResult


router = APIRouter()


class YouTubeRequest:
    def __init__(self, url: str):
        self.url = url


async def validated_file_content(file: UploadFile = File(...)) -> tuple[bytes, str]:
    validate_upload(file)
    content = await file.read()
    return content, file.filename or ""


@router.post("/extract/pdf")
async def extract_from_pdf(file: UploadFile = File(...)):
    validate_upload(file)
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    content = await file.read()
    result = await extract_content(content, file.filename)
    return result.model_dump()


@router.post("/extract/image")
async def extract_from_image(
    file_data: tuple[bytes, str] = Depends(validated_file_content)
):
    content, filename = file_data
    result = await extract_content(content, filename)
    return result.model_dump()


@router.post("/extract/audio")
async def extract_from_audio(
    file_data: tuple[bytes, str] = Depends(validated_file_content)
):
    content, filename = file_data
    result = await extract_content(content, filename)
    return result.model_dump()


@router.post("/extract/youtube")
async def extract_from_youtube(url: str):
    result = await extract_youtube(url)

    if result.error:
        raise HTTPException(status_code=400, detail=result.error)

    return result.model_dump()


