from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from dataclasses import asdict

from ...domain.models.persistence import PersistedChunk
from ...domain.ports.chunk_repository import ChunkRepositoryPort


class MongoChunkRepository(ChunkRepositoryPort):
    def __init__(self, uri: str, database: str, collection: str = "chunks") -> None:
        from pymongo import MongoClient

        self._client = MongoClient(uri)
        self._collection = self._client[database][collection]
        self._collection.create_index("document_id")
        self._collection.create_index("expiresAt")

    async def stage_chunks(self, document_id: str, chunks: list[PersistedChunk], ttl_seconds: int) -> None:
        await asyncio.to_thread(self._stage_sync, document_id, chunks, ttl_seconds)

    async def commit_document(self, document_id: str) -> None:
        await asyncio.to_thread(
            self._collection.update_many,
            {"document_id": document_id},
            {"$set": {"status": "committed"}, "$unset": {"expiresAt": ""}},
        )

    async def rollback_document(self, document_id: str) -> None:
        await asyncio.to_thread(self._collection.delete_many, {"document_id": document_id})

    def _stage_sync(self, document_id: str, chunks: list[PersistedChunk], ttl_seconds: int) -> None:
        expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds) if ttl_seconds > 0 else None
        payloads = []
        for chunk in chunks:
            item = asdict(chunk)
            item["document_id"] = document_id
            item["status"] = "staged"
            if expires_at is not None:
                item["expiresAt"] = expires_at
            payloads.append(item)

        if payloads:
            self._collection.insert_many(payloads)

