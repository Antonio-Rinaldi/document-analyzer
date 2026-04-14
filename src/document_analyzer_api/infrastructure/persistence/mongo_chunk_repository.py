"""Detailed module documentation for `src/document_analyzer_api/infrastructure/persistence/mongo_chunk_repository.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `mongo_chunk_repository.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: MongoChunkRepository.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from dataclasses import asdict

from ...domain.models.persistence import PersistedChunk
from ...domain.ports.chunk_repository import ChunkRepositoryPort


class MongoChunkRepository(ChunkRepositoryPort):
    """Detailed class documentation for `MongoChunkRepository`.
    
    This repository adapter belongs to `src/document_analyzer_api/infrastructure/persistence/mongo_chunk_repository.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, uri: str, database: str, collection: str = "chunks") -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chunk_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                uri: Input parameter for `__init__`.
                database: Input parameter for `__init__`.
                collection: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        from pymongo import MongoClient

        self._client = MongoClient(uri)
        self._collection = self._client[database][collection]
        self._collection.create_index("document_id")
        self._collection.create_index("expiresAt")

    async def stage_chunks(self, document_id: str, chunks: list[PersistedChunk], ttl_seconds: int) -> None:
        """Detailed asynchronous function documentation for `stage_chunks`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chunk_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                document_id: Input parameter for `stage_chunks`.
                chunks: Input parameter for `stage_chunks`.
                ttl_seconds: Input parameter for `stage_chunks`.
        
            Returns:
                Value defined by `stage_chunks` contract and consumed by downstream callers.
        """
        await asyncio.to_thread(self._stage_sync, document_id, chunks, ttl_seconds)

    async def commit_document(self, document_id: str) -> None:
        """Detailed asynchronous function documentation for `commit_document`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chunk_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                document_id: Input parameter for `commit_document`.
        
            Returns:
                Value defined by `commit_document` contract and consumed by downstream callers.
        """
        await asyncio.to_thread(
            self._collection.update_many,
            {"document_id": document_id},
            {"$set": {"status": "committed"}, "$unset": {"expiresAt": ""}},
        )

    async def rollback_document(self, document_id: str) -> None:
        """Detailed asynchronous function documentation for `rollback_document`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chunk_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                document_id: Input parameter for `rollback_document`.
        
            Returns:
                Value defined by `rollback_document` contract and consumed by downstream callers.
        """
        await asyncio.to_thread(self._collection.delete_many, {"document_id": document_id})

    def _stage_sync(self, document_id: str, chunks: list[PersistedChunk], ttl_seconds: int) -> None:
        """Detailed synchronous function documentation for `_stage_sync`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chunk_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                document_id: Input parameter for `_stage_sync`.
                chunks: Input parameter for `_stage_sync`.
                ttl_seconds: Input parameter for `_stage_sync`.
        
            Returns:
                Value defined by `_stage_sync` contract and consumed by downstream callers.
        """
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

