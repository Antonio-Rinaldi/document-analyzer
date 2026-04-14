"""Detailed module documentation for `src/document_analyzer_api/infrastructure/persistence/local_document_metadata_repository.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `local_document_metadata_repository.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: LocalDocumentMetadataRepository.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

import asyncio
import json
from dataclasses import asdict
from pathlib import Path

from ...domain.models.persistence import DocumentMetadata
from ...domain.ports.document_metadata_repository import DocumentMetadataRepositoryPort


class LocalDocumentMetadataRepository(DocumentMetadataRepositoryPort):
    """Detailed class documentation for `LocalDocumentMetadataRepository`.
    
    This repository adapter belongs to `src/document_analyzer_api/infrastructure/persistence/local_document_metadata_repository.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, root_path: str) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_document_metadata_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                root_path: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._file_path = Path(root_path) / "documents.json"

    async def upsert(self, document: DocumentMetadata) -> None:
        """Detailed asynchronous function documentation for `upsert`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_document_metadata_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                document: Input parameter for `upsert`.
        
            Returns:
                Value defined by `upsert` contract and consumed by downstream callers.
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
        """Detailed asynchronous function documentation for `list_paginated`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_document_metadata_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Collects and returns a paginated or aggregated list of entities.
        
            Args:
                offset: Input parameter for `list_paginated`.
                limit: Input parameter for `list_paginated`.
        
            Returns:
                Value defined by `list_paginated` contract and consumed by downstream callers.
        """
        records = await self._load_records()
        total = len(records)
        items = [DocumentMetadata(**item) for item in records[offset : offset + limit]]
        return items, total

    async def _load_records(self) -> list[dict]:
        """Detailed asynchronous function documentation for `_load_records`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_document_metadata_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `_load_records` contract and consumed by downstream callers.
        """
        def _read() -> list[dict]:
            """Detailed synchronous function documentation for `_read`.
            
            This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_document_metadata_repository.py` and contributes to the module workflow
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

    async def _save_records(self, records: list[dict]) -> None:
        """Detailed asynchronous function documentation for `_save_records`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_document_metadata_repository.py` and contributes to the module workflow
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
            
            This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_document_metadata_repository.py` and contributes to the module workflow
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

