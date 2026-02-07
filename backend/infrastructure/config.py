from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


Environment = Literal["development", "staging", "production"]


class Settings(BaseSettings):
    google_api_key: str = ""
    deepgram_api_key: str = ""

    environment: Environment = "development"
    debug: bool = True

    llm_model: str = "gemini-2.0-flash-exp"
    temperature: float = 0.3
    max_tokens: int = 8192

    max_file_size_mb: int = 50
    content_max_length: int = 50000

    allowed_mime_types: list[str] = [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "audio/wav",
        "audio/mpeg",
        "audio/mp3",
    ]

    deepgram_timeout_sec: float = 60.0
    genai_timeout_sec: float = 30.0

    ambiguity_confidence_threshold: float = 0.7

    cors_origins: list[str] = ["*"]
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60

    log_level: str = "INFO"
    log_json: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

