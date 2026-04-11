from ...domain.models.persistence import DocumentMetadata
from ...domain.ports.document_metadata_repository import DocumentMetadataRepositoryPort


class DocumentQueryService:
    def __init__(self, metadata_repository: DocumentMetadataRepositoryPort) -> None:
        self._metadata_repository = metadata_repository

    async def list_documents(self, offset: int, limit: int) -> tuple[list[DocumentMetadata], int]:
        return await self._metadata_repository.list_paginated(offset=offset, limit=limit)

