from fastapi import HTTPException, UploadFile
from functools import wraps
from typing import Callable

from infrastructure.config import get_settings


def validate_upload(file: UploadFile) -> None:
    settings = get_settings()

    if file.content_type and file.content_type not in settings.allowed_mime_types:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file.content_type}"
        )

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    if size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
        )
