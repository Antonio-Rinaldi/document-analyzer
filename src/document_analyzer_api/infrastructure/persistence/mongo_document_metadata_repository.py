from __future__ import annotations

import asyncio

from ...domain.models.persistence import DocumentMetadata
from ...domain.ports.document_metadata_repository import DocumentMetadataRepositoryPort


class MongoDocumentMetadataRepository(DocumentMetadataRepositoryPort):
    def __init__(self, uri: str, database: str, collection: str = "documents") -> None:
        from pymongo import MongoClient

        self._client = MongoClient(uri)
        self._collection = self._client[database][collection]
        self._collection.create_index("id", unique=True)

    async def upsert(self, document: DocumentMetadata) -> None:
        await asyncio.to_thread(
            self._collection.update_one,
            {"id": document.id},
            {"$set": {"id": document.id, "name": document.name, "description": document.description}},
            True,
        )

    async def list_paginated(self, offset: int, limit: int) -> tuple[list[DocumentMetadata], int]:
        def _read() -> tuple[list[DocumentMetadata], int]:
            total = self._collection.count_documents({})
            cursor = self._collection.find({}, {"_id": 0}).sort("id", 1).skip(offset).limit(limit)
            items = [DocumentMetadata(**item) for item in cursor]
            return items, total

        return await asyncio.to_thread(_read)

