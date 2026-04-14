"""Module `src/document_analyzer_api/infrastructure/persistence/local_chunk_repository.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: LocalChunkRepository.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
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
    """LocalChunkRepository repository adapter.
    
    This class is defined in `src/document_analyzer_api/infrastructure/persistence/local_chunk_repository.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, root_path: str, backend_name: str) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chunk_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (Path) to satisfy the callable contract.
        
            Args:
                root_path: Input parameter accepted by `__init__`.
                backend_name: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._file_path = Path(root_path) / f"{backend_name}_chunks.json"

    async def stage_chunks(self, document_id: str, chunks: list[PersistedChunk], ttl_seconds: int) -> None:
        """Asynchronous execution path for `stage_chunks`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chunk_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (_load_records, _save_records, append, asdict) to satisfy the callable contract.
        
            Args:
                document_id: Input parameter accepted by `stage_chunks`.
                chunks: Input parameter accepted by `stage_chunks`.
                ttl_seconds: Input parameter accepted by `stage_chunks`.
        
            Returns:
                A value compatible with `None`.
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
        """Asynchronous execution path for `commit_document`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chunk_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (_load_records, _save_records, get) to satisfy the callable contract.
        
            Args:
                document_id: Input parameter accepted by `commit_document`.
        
            Returns:
                A value compatible with `None`.
        """
        records = await self._load_records()
        for record in records:
            if record.get("document_id") == document_id:
                record["status"] = "committed"
                record["expiresAt"] = None
        await self._save_records(records)

    async def rollback_document(self, document_id: str) -> None:
        """Asynchronous execution path for `rollback_document`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chunk_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (_load_records, _save_records, get) to satisfy the callable contract.
        
            Args:
                document_id: Input parameter accepted by `rollback_document`.
        
            Returns:
                A value compatible with `None`.
        """
        records = await self._load_records()
        filtered = [item for item in records if item.get("document_id") != document_id]
        await self._save_records(filtered)

    async def _load_records(self) -> list[dict[str, Any]]:
        """Asynchronous execution path for `_load_records`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chunk_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (exists, loads, read_text, to_thread) to satisfy the callable contract.
        
            Args:
                None.
        
            Returns:
                A value compatible with `list[dict[str, Any]]`.
        """
        def _read() -> list[dict[str, Any]]:
            """Synchronous execution path for `_read`.
            
            This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chunk_repository.py` and contributes to module-level behavior
            with explicit and testable execution semantics.
            
                Behavior:
                    Coordinates helper calls (exists, loads, read_text) to satisfy the callable contract.
            
                Args:
                    None.
            
                Returns:
                    A value compatible with `list[dict[str, Any]]`.
            """
            if not self._file_path.exists():
                return []
            return json.loads(self._file_path.read_text(encoding="utf-8"))

        return await asyncio.to_thread(_read)

    async def _save_records(self, records: list[dict[str, Any]]) -> None:
        """Asynchronous execution path for `_save_records`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chunk_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (dumps, mkdir, to_thread, write_text) to satisfy the callable contract.
        
            Args:
                records: Input parameter accepted by `_save_records`.
        
            Returns:
                A value compatible with `None`.
        """
        def _write() -> None:
            """Synchronous execution path for `_write`.
            
            This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chunk_repository.py` and contributes to module-level behavior
            with explicit and testable execution semantics.
            
                Behavior:
                    Coordinates helper calls (dumps, mkdir, write_text) to satisfy the callable contract.
            
                Args:
                    None.
            
                Returns:
                    A value compatible with `None`.
            """
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            self._file_path.write_text(json.dumps(records), encoding="utf-8")

        await asyncio.to_thread(_write)

