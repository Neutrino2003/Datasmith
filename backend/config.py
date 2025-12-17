from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""
    google_api_key: str = ""
    deepgram_api_key: str = ""
    debug: bool = True
    max_file_size_mb: int = 50
    llm_model: str = "models/gemini-3-flash-preview"
    temperature: float = 0.3
    ambiguity_confidence_threshold: float = 0.7
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra env vars not defined above
    
    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    return Settings()
