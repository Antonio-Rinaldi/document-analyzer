from typing import Protocol

from ..models.persistence import DocumentMetadata


class DocumentMetadataRepositoryPort(Protocol):
    async def upsert(self, document: DocumentMetadata) -> None:
        ...

    async def list_paginated(self, offset: int, limit: int) -> tuple[list[DocumentMetadata], int]:
        ...

