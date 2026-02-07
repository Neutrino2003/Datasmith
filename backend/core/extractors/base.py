from abc import ABC, abstractmethod
from typing import Callable, Awaitable

from schemas import ExtractionResult


ExtractorFunc = Callable[[bytes, str | None], Awaitable[ExtractionResult]]


class ExtractorRegistry:
    _extractors: dict[str, ExtractorFunc] = {}
    _extension_map: dict[str, str] = {}

    @classmethod
    def register(cls, file_type: str, extensions: list[str]):
        def decorator(func: ExtractorFunc) -> ExtractorFunc:
            cls._extractors[file_type] = func
            for ext in extensions:
                cls._extension_map[ext.lower()] = file_type
            return func
        return decorator

    @classmethod
    def get_extractor(cls, filename: str | None) -> ExtractorFunc | None:
        if not filename:
            return None
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        file_type = cls._extension_map.get(ext)
        return cls._extractors.get(file_type) if file_type else None

    @classmethod
    def get_by_type(cls, file_type: str) -> ExtractorFunc | None:
        return cls._extractors.get(file_type)
