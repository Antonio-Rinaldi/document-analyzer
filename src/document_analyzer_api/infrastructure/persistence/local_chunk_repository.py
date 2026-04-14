"""Detailed module documentation for `src/document_analyzer_api/infrastructure/persistence/local_chunk_repository.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `local_chunk_repository.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: LocalChunkRepository.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

import asyncio
import json
from dataclasses import asdict
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from ...domain.models.persistence import PersistedChunk
from ...domain.ports.chunk_repository import ChunkRepositoryPort


class LocalChunkRepository(ChunkRepositoryPort):
    """Detailed class documentation for `LocalChunkRepository`.
    
    This repository adapter belongs to `src/document_analyzer_api/infrastructure/persistence/local_chunk_repository.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, root_path: str, backend_name: str) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chunk_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                root_path: Input parameter for `__init__`.
                backend_name: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._file_path = Path(root_path) / f"{backend_name}_chunks.json"

    async def stage_chunks(self, document_id: str, chunks: list[PersistedChunk], ttl_seconds: int) -> None:
        """Detailed asynchronous function documentation for `stage_chunks`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chunk_repository.py` and contributes to the module workflow
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
        records = await self._load_records()
        expires_at = (datetime.now(UTC) + timedelta(seconds=ttl_seconds)).isoformat() if ttl_seconds > 0 else None

        for chunk in chunks:
            payload = asdict(chunk)
            payload["status"] = "staged"
            payload["expiresAt"] = expires_at
            records.append(payload)

        await self._save_records(records)

    async def commit_document(self, document_id: str) -> None:
        """Detailed asynchronous function documentation for `commit_document`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chunk_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                document_id: Input parameter for `commit_document`.
        
            Returns:
                Value defined by `commit_document` contract and consumed by downstream callers.
        """
        records = await self._load_records()
        for record in records:
            if record.get("document_id") == document_id:
                record["status"] = "committed"
                record["expiresAt"] = None
        await self._save_records(records)

    async def rollback_document(self, document_id: str) -> None:
        """Detailed asynchronous function documentation for `rollback_document`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chunk_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                document_id: Input parameter for `rollback_document`.
        
            Returns:
                Value defined by `rollback_document` contract and consumed by downstream callers.
        """
        records = await self._load_records()
        filtered = [item for item in records if item.get("document_id") != document_id]
        await self._save_records(filtered)

    async def _load_records(self) -> list[dict[str, Any]]:
        """Detailed asynchronous function documentation for `_load_records`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chunk_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `_load_records` contract and consumed by downstream callers.
        """
        def _read() -> list[dict[str, Any]]:
            """Detailed synchronous function documentation for `_read`.
            
            This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chunk_repository.py` and contributes to the module workflow
            through deterministic input/output behavior and explicit collaboration contracts.
            
                Behavior:
                    Executes the callable contract for this module responsibility.
            
                Args:
                    None.
            
                Returns:
                    Value defined by `_read` contract and consumed by downstream callers.
            """
            if not self._file_path.exists():
                return []
            return json.loads(self._file_path.read_text(encoding="utf-8"))

        return await asyncio.to_thread(_read)

    async def _save_records(self, records: list[dict[str, Any]]) -> None:
        """Detailed asynchronous function documentation for `_save_records`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chunk_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                records: Input parameter for `_save_records`.
        
            Returns:
                Value defined by `_save_records` contract and consumed by downstream callers.
        """
        def _write() -> None:
            """Detailed synchronous function documentation for `_write`.
            
            This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chunk_repository.py` and contributes to the module workflow
            through deterministic input/output behavior and explicit collaboration contracts.
            
                Behavior:
                    Executes the callable contract for this module responsibility.
            
                Args:
                    None.
            
                Returns:
                    Value defined by `_write` contract and consumed by downstream callers.
            """
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            self._file_path.write_text(json.dumps(records), encoding="utf-8")

        await asyncio.to_thread(_write)

