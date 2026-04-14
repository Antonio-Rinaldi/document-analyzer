"""Module `src/document_analyzer_api/application/services/document_query_service.py`.

This module belongs to the application service layer of Document Analyzer.

Purpose:
- Coordinates use-case workflows over domain ports and adapters.

Defined symbols:
- Classes: DocumentQueryService.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from ...domain.models.persistence import DocumentMetadata
from ...domain.ports.document_metadata_repository import DocumentMetadataRepositoryPort


class DocumentQueryService:
    """DocumentQueryService application service.
    
    This class is defined in `src/document_analyzer_api/application/services/document_query_service.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, metadata_repository: DocumentMetadataRepositoryPort) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_query_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                metadata_repository: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._metadata_repository = metadata_repository

    async def list_documents(self, offset: int, limit: int) -> tuple[list[DocumentMetadata], int]:
        """Asynchronous execution path for `list_documents`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_query_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Collects and returns a list or paginated subset of entities.
        
            Args:
                offset: Input parameter accepted by `list_documents`.
                limit: Input parameter accepted by `list_documents`.
        
            Returns:
                A value compatible with `tuple[list[DocumentMetadata], int]`.
        """
        return await self._metadata_repository.list_paginated(offset=offset, limit=limit)

