"""Detailed module documentation for `src/document_analyzer_api/infrastructure/persistence/mongo_document_metadata_repository.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `mongo_document_metadata_repository.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: MongoDocumentMetadataRepository.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from __future__ import annotations

import asyncio

from ...domain.models.persistence import DocumentMetadata
from ...domain.ports.document_metadata_repository import DocumentMetadataRepositoryPort


class MongoDocumentMetadataRepository(DocumentMetadataRepositoryPort):
    """Detailed class documentation for `MongoDocumentMetadataRepository`.
    
    This repository adapter belongs to `src/document_analyzer_api/infrastructure/persistence/mongo_document_metadata_repository.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, uri: str, database: str, collection: str = "documents") -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_document_metadata_repository.py` and contributes to the module workflow
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
        self._collection.create_index("id", unique=True)

    async def upsert(self, document: DocumentMetadata) -> None:
        """Detailed asynchronous function documentation for `upsert`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_document_metadata_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                document: Input parameter for `upsert`.
        
            Returns:
                Value defined by `upsert` contract and consumed by downstream callers.
        """
        await asyncio.to_thread(
            self._collection.update_one,
            {"id": document.id},
            {"$set": {"id": document.id, "name": document.name, "description": document.description}},
            True,
        )

    async def list_paginated(self, offset: int, limit: int) -> tuple[list[DocumentMetadata], int]:
        """Detailed asynchronous function documentation for `list_paginated`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_document_metadata_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Collects and returns a paginated or aggregated list of entities.
        
            Args:
                offset: Input parameter for `list_paginated`.
                limit: Input parameter for `list_paginated`.
        
            Returns:
                Value defined by `list_paginated` contract and consumed by downstream callers.
        """
        def _read() -> tuple[list[DocumentMetadata], int]:
            """Detailed synchronous function documentation for `_read`.
            
            This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_document_metadata_repository.py` and contributes to the module workflow
            through deterministic input/output behavior and explicit collaboration contracts.
            
                Behavior:
                    Executes the callable contract for this module responsibility.
            
                Args:
                    None.
            
                Returns:
                    Value defined by `_read` contract and consumed by downstream callers.
            """
            total = self._collection.count_documents({})
            cursor = self._collection.find({}, {"_id": 0}).sort("id", 1).skip(offset).limit(limit)
            items = [DocumentMetadata(**item) for item in cursor]
            return items, total

        return await asyncio.to_thread(_read)

