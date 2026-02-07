import asyncio
from abc import ABC, abstractmethod
from typing import TypeVar

from infrastructure.llm.stats import TokenStats

T = TypeVar("T")


class BaseSessionManager(ABC):
    @abstractmethod
    async def get_stats(self, session_id: str, model: str) -> TokenStats:
        pass

    @abstractmethod
    async def reset(self, session_id: str) -> bool:
        pass

    @abstractmethod
    async def get_all_session_ids(self) -> list[str]:
        pass


class InMemorySessionManager(BaseSessionManager):
    """In-memory session manager for single-worker deployments only.
    
    WARNING: Do not use with multiple workers (--workers > 1).
    For multi-worker deployments, use RedisSessionManager.
    """

    def __init__(self):
        self._sessions: dict[str, TokenStats] = {}
        self._lock = asyncio.Lock()

    async def get_stats(self, session_id: str, model: str) -> TokenStats:
        async with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = TokenStats(model=model)
            return self._sessions[session_id]

    async def reset(self, session_id: str) -> bool:
        async with self._lock:
            return self._sessions.pop(session_id, None) is not None

    async def get_all_session_ids(self) -> list[str]:
        async with self._lock:
            return list(self._sessions.keys())


SessionManager = InMemorySessionManager

