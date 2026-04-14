"""Module `src/document_analyzer_api/infrastructure/persistence/mongo_chunk_repository.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: MongoChunkRepository.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from dataclasses import asdict

from ...domain.models.persistence import PersistedChunk
from ...domain.ports.chunk_repository import ChunkRepositoryPort


class MongoChunkRepository(ChunkRepositoryPort):
    """MongoChunkRepository repository adapter.
    
    This class is defined in `src/document_analyzer_api/infrastructure/persistence/mongo_chunk_repository.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, uri: str, database: str, collection: str = "chunks") -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chunk_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (MongoClient, create_index) to satisfy the callable contract.
        
            Args:
                uri: Input parameter accepted by `__init__`.
                database: Input parameter accepted by `__init__`.
                collection: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        from pymongo import MongoClient

        self._client = MongoClient(uri)
        self._collection = self._client[database][collection]
        self._collection.create_index("document_id")
        self._collection.create_index("expiresAt")

    async def stage_chunks(self, document_id: str, chunks: list[PersistedChunk], ttl_seconds: int) -> None:
        """Asynchronous execution path for `stage_chunks`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chunk_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (to_thread) to satisfy the callable contract.
        
            Args:
                document_id: Input parameter accepted by `stage_chunks`.
                chunks: Input parameter accepted by `stage_chunks`.
                ttl_seconds: Input parameter accepted by `stage_chunks`.
        
            Returns:
                A value compatible with `None`.
        """
        await asyncio.to_thread(self._stage_sync, document_id, chunks, ttl_seconds)

    async def commit_document(self, document_id: str) -> None:
        """Asynchronous execution path for `commit_document`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chunk_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (to_thread) to satisfy the callable contract.
        
            Args:
                document_id: Input parameter accepted by `commit_document`.
        
            Returns:
                A value compatible with `None`.
        """
        await asyncio.to_thread(
            self._collection.update_many,
            {"document_id": document_id},
            {"$set": {"status": "committed"}, "$unset": {"expiresAt": ""}},
        )

    async def rollback_document(self, document_id: str) -> None:
        """Asynchronous execution path for `rollback_document`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chunk_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (to_thread) to satisfy the callable contract.
        
            Args:
                document_id: Input parameter accepted by `rollback_document`.
        
            Returns:
                A value compatible with `None`.
        """
        await asyncio.to_thread(self._collection.delete_many, {"document_id": document_id})

    def _stage_sync(self, document_id: str, chunks: list[PersistedChunk], ttl_seconds: int) -> None:
        """Synchronous execution path for `_stage_sync`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chunk_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (append, asdict, insert_many, now) to satisfy the callable contract.
        
            Args:
                document_id: Input parameter accepted by `_stage_sync`.
                chunks: Input parameter accepted by `_stage_sync`.
                ttl_seconds: Input parameter accepted by `_stage_sync`.
        
            Returns:
                A value compatible with `None`.
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

