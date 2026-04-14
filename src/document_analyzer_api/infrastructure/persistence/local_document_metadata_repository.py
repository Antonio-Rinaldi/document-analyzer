"""Module `src/document_analyzer_api/infrastructure/persistence/local_document_metadata_repository.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: LocalDocumentMetadataRepository.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import asyncio
import json
from dataclasses import asdict
from pathlib import Path

from ...domain.models.persistence import DocumentMetadata
from ...domain.ports.document_metadata_repository import DocumentMetadataRepositoryPort


class LocalDocumentMetadataRepository(DocumentMetadataRepositoryPort):
    """LocalDocumentMetadataRepository repository adapter.
    
    This class is defined in `src/document_analyzer_api/infrastructure/persistence/local_document_metadata_repository.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, root_path: str) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_document_metadata_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (Path) to satisfy the callable contract.
        
            Args:
                root_path: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._file_path = Path(root_path) / "documents.json"

    async def upsert(self, document: DocumentMetadata) -> None:
        """Asynchronous execution path for `upsert`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_document_metadata_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (_load_records, _save_records, append, asdict) to satisfy the callable contract.
        
            Args:
                document: Input parameter accepted by `upsert`.
        
            Returns:
                A value compatible with `None`.
        """
        records = await self._load_records()
        data = asdict(document)
        idx = next((i for i, item in enumerate(records) if item.get("id") == document.id), None)
        if idx is None:
            records.append(data)
        else:
            records[idx] = data
        await self._save_records(records)

    async def list_paginated(self, offset: int, limit: int) -> tuple[list[DocumentMetadata], int]:
        """Asynchronous execution path for `list_paginated`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_document_metadata_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Collects and returns a list or paginated subset of entities.
        
            Args:
                offset: Input parameter accepted by `list_paginated`.
                limit: Input parameter accepted by `list_paginated`.
        
            Returns:
                A value compatible with `tuple[list[DocumentMetadata], int]`.
        """
        records = await self._load_records()
        total = len(records)
        items = [DocumentMetadata(**item) for item in records[offset : offset + limit]]
        return items, total

    async def _load_records(self) -> list[dict]:
        """Asynchronous execution path for `_load_records`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_document_metadata_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (exists, loads, read_text, to_thread) to satisfy the callable contract.
        
            Args:
                None.
        
            Returns:
                A value compatible with `list[dict]`.
        """
        def _read() -> list[dict]:
            """Synchronous execution path for `_read`.
            
            This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_document_metadata_repository.py` and contributes to module-level behavior
            with explicit and testable execution semantics.
            
                Behavior:
                    Coordinates helper calls (exists, loads, read_text) to satisfy the callable contract.
            
                Args:
                    None.
            
                Returns:
                    A value compatible with `list[dict]`.
            """
            if not self._file_path.exists():
                return []
            return json.loads(self._file_path.read_text(encoding="utf-8"))

        return await asyncio.to_thread(_read)

    async def _save_records(self, records: list[dict]) -> None:
        """Asynchronous execution path for `_save_records`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_document_metadata_repository.py` and contributes to module-level behavior
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
            
            This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_document_metadata_repository.py` and contributes to module-level behavior
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

