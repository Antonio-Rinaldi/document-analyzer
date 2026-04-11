from typing import Protocol

from ..models.persistence import PersistedChunk


class ChunkRepositoryPort(Protocol):
    async def stage_chunks(self, document_id: str, chunks: list[PersistedChunk], ttl_seconds: int) -> None:
        ...

    async def commit_document(self, document_id: str) -> None:
        ...

    async def rollback_document(self, document_id: str) -> None:
        ...

