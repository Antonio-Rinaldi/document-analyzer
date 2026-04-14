"""Detailed module documentation for `src/document_analyzer_api/application/services/document_query_service.py`.

File role:
- Located in the application service layer.
- Defines logic and symbols for `document_query_service.py` within Document Analyzer V1.

Purpose:
- Implements use-case orchestration across domain ports and infrastructure adapters.

Exported symbols overview:
- Classes: DocumentQueryService.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from ...domain.models.persistence import DocumentMetadata
from ...domain.ports.document_metadata_repository import DocumentMetadataRepositoryPort


class DocumentQueryService:
    """Detailed class documentation for `DocumentQueryService`.
    
    This application service belongs to `src/document_analyzer_api/application/services/document_query_service.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, metadata_repository: DocumentMetadataRepositoryPort) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_query_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                metadata_repository: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._metadata_repository = metadata_repository

    async def list_documents(self, offset: int, limit: int) -> tuple[list[DocumentMetadata], int]:
        """Detailed asynchronous function documentation for `list_documents`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_query_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Collects and returns a paginated or aggregated list of entities.
        
            Args:
                offset: Input parameter for `list_documents`.
                limit: Input parameter for `list_documents`.
        
            Returns:
                Value defined by `list_documents` contract and consumed by downstream callers.
        """
        return await self._metadata_repository.list_paginated(offset=offset, limit=limit)

