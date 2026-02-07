from functools import lru_cache

from google import genai
import httpx

from infrastructure.config import get_settings
from infrastructure.session_manager import SessionManager


@lru_cache()
def get_genai_client() -> genai.Client:
    settings = get_settings()
    return genai.Client(api_key=settings.google_api_key)


_httpx_client: httpx.AsyncClient | None = None


async def get_httpx_client() -> httpx.AsyncClient:
    global _httpx_client
    if _httpx_client is None:
        settings = get_settings()
        _httpx_client = httpx.AsyncClient(timeout=settings.deepgram_timeout_sec)
    return _httpx_client


async def close_httpx_client():
    global _httpx_client
    if _httpx_client:
        await _httpx_client.aclose()
        _httpx_client = None


_session_manager: SessionManager | None = None


def get_session_manager() -> SessionManager:
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
