"""Module `src/document_analyzer_api/infrastructure/persistence/mongo_document_metadata_repository.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: MongoDocumentMetadataRepository.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from __future__ import annotations

import asyncio

from ...domain.models.persistence import DocumentMetadata
from ...domain.ports.document_metadata_repository import DocumentMetadataRepositoryPort


class MongoDocumentMetadataRepository(DocumentMetadataRepositoryPort):
    """MongoDocumentMetadataRepository repository adapter.
    
    This class is defined in `src/document_analyzer_api/infrastructure/persistence/mongo_document_metadata_repository.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, uri: str, database: str, collection: str = "documents") -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_document_metadata_repository.py` and contributes to module-level behavior
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
        self._collection.create_index("id", unique=True)

    async def upsert(self, document: DocumentMetadata) -> None:
        """Asynchronous execution path for `upsert`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_document_metadata_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (to_thread) to satisfy the callable contract.
        
            Args:
                document: Input parameter accepted by `upsert`.
        
            Returns:
                A value compatible with `None`.
        """
        await asyncio.to_thread(
            self._collection.update_one,
            {"id": document.id},
            {"$set": {"id": document.id, "name": document.name, "description": document.description}},
            True,
        )

    async def list_paginated(self, offset: int, limit: int) -> tuple[list[DocumentMetadata], int]:
        """Asynchronous execution path for `list_paginated`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_document_metadata_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Collects and returns a list or paginated subset of entities.
        
            Args:
                offset: Input parameter accepted by `list_paginated`.
                limit: Input parameter accepted by `list_paginated`.
        
            Returns:
                A value compatible with `tuple[list[DocumentMetadata], int]`.
        """
        def _read() -> tuple[list[DocumentMetadata], int]:
            """Synchronous execution path for `_read`.
            
            This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_document_metadata_repository.py` and contributes to module-level behavior
            with explicit and testable execution semantics.
            
                Behavior:
                    Coordinates helper calls (DocumentMetadata, count_documents, find, limit) to satisfy the callable contract.
            
                Args:
                    None.
            
                Returns:
                    A value compatible with `tuple[list[DocumentMetadata], int]`.
            """
            total = self._collection.count_documents({})
            cursor = self._collection.find({}, {"_id": 0}).sort("id", 1).skip(offset).limit(limit)
            items = [DocumentMetadata(**item) for item in cursor]
            return items, total

        return await asyncio.to_thread(_read)

