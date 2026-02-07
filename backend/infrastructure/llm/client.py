from functools import lru_cache
from langchain_google_genai import ChatGoogleGenerativeAI
from infrastructure.config import get_settings


@lru_cache()
def get_llm_client() -> ChatGoogleGenerativeAI:
    settings = get_settings()
    return ChatGoogleGenerativeAI(
        model=settings.llm_model,
        google_api_key=settings.google_api_key,
        temperature=settings.temperature,
        max_output_tokens=settings.max_tokens
    )
