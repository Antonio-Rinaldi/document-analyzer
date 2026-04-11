from typing import Protocol

from ..models.chat import ChatSession


class ChatSessionRepositoryPort(Protocol):
    async def create(self, session_id: str, ttl_seconds: int) -> ChatSession:
        ...

    async def get(self, session_id: str) -> ChatSession | None:
        ...

    async def upsert(self, session: ChatSession, ttl_seconds: int) -> None:
        ...

    async def delete(self, session_id: str) -> bool:
        ...

