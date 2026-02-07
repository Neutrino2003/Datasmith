from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from pydantic import BaseModel
from typing import Optional

from core.agents.coordinator import CoordinatorAgent
from core.extractors.extractor import extract_content
from infrastructure.config import get_settings, Settings
from infrastructure.dependencies import get_session_manager
from infrastructure.session_manager import SessionManager
from infrastructure.llm.client import get_llm_client


router = APIRouter()

_coordinator: CoordinatorAgent | None = None


def get_coordinator() -> CoordinatorAgent:
    global _coordinator
    if _coordinator is None:
        _coordinator = CoordinatorAgent()
    return _coordinator


class AnalyzeRequest(BaseModel):
    text: Optional[str] = None
    session_id: str = "default"


class AnalyzeResponse(BaseModel):
    response: str
    requires_clarification: bool
    stats: dict


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(
    request: AnalyzeRequest,
    coordinator: CoordinatorAgent = Depends(get_coordinator),
    session_mgr: SessionManager = Depends(get_session_manager),
    settings: Settings = Depends(get_settings)
):
    if not request.text:
        raise HTTPException(status_code=400, detail="Text is required")

    stats = await session_mgr.get_stats(request.session_id, settings.llm_model)
    result = await coordinator.process(
        session_id=request.session_id,
        stats=stats,
        message=request.text,
        extracted_text=None
    )

    return AnalyzeResponse(**result)


@router.post("/analyze/file", response_model=AnalyzeResponse)
async def analyze_file(
    file: UploadFile = File(...),
    session_id: str = Form("default"),
    message: Optional[str] = Form(None),
    coordinator: CoordinatorAgent = Depends(get_coordinator),
    session_mgr: SessionManager = Depends(get_session_manager),
    settings: Settings = Depends(get_settings)
):
    from api.middleware.validation import validate_upload
    validate_upload(file)

    content = await file.read()
    extraction = await extract_content(content, file.filename)

    if extraction.error:
        raise HTTPException(status_code=400, detail=extraction.error)

    stats = await session_mgr.get_stats(session_id, settings.llm_model)
    result = await coordinator.process(
        session_id=session_id,
        stats=stats,
        message=message,
        extracted_text=extraction.extracted_text
    )

    return AnalyzeResponse(**result)


@router.post("/analyze/upload", response_model=AnalyzeResponse)
async def analyze_upload(
    files: list[UploadFile] = File(default=[]),
    text: str = Form(""),
    session_id: str = Form("default"),
    coordinator: CoordinatorAgent = Depends(get_coordinator),
    session_mgr: SessionManager = Depends(get_session_manager),
    settings: Settings = Depends(get_settings)
):
    """Analyze text with optional multiple file uploads."""
    from api.middleware.validation import validate_upload
    
    extracted_texts = []
    
    # Process each uploaded file
    for file in files:
        validate_upload(file)
        content = await file.read()
        extraction = await extract_content(content, file.filename)
        
        if extraction.error:
            # Continue with other files, log error
            extracted_texts.append(f"[Error processing {file.filename}: {extraction.error}]")
        elif extraction.extracted_text:
            extracted_texts.append(f"[From {file.filename}]:\n{extraction.extracted_text}")
    
    # Combine all extracted text
    combined_extraction = "\n\n".join(extracted_texts) if extracted_texts else None
    
    # If no text and no valid extractions, error
    if not text.strip() and not combined_extraction:
        raise HTTPException(status_code=400, detail="Please provide text or valid files")
    
    stats = await session_mgr.get_stats(session_id, settings.llm_model)
    result = await coordinator.process(
        session_id=session_id,
        stats=stats,
        message=text,
        extracted_text=combined_extraction
    )

    return AnalyzeResponse(**result)


@router.post("/reset/{session_id}")
async def reset_session(
    session_id: str,
    session_mgr: SessionManager = Depends(get_session_manager)
):
    await session_mgr.reset(session_id)
    return {"status": "reset", "session_id": session_id}


@router.get("/stats/{session_id}")
async def get_stats(
    session_id: str,
    session_mgr: SessionManager = Depends(get_session_manager),
    settings: Settings = Depends(get_settings)
):
    stats = await session_mgr.get_stats(session_id, settings.llm_model)
    return stats.to_dict()

