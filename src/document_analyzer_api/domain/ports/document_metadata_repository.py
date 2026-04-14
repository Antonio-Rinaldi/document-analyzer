"""Detailed module documentation for `src/document_analyzer_api/domain/ports/document_metadata_repository.py`.

File role:
- Located in the domain port layer.
- Defines logic and symbols for `document_metadata_repository.py` within Document Analyzer V1.

Purpose:
- Declares abstract contracts implemented by infrastructure adapters.

Exported symbols overview:
- Classes: DocumentMetadataRepositoryPort.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from typing import Protocol

from ..models.persistence import DocumentMetadata


class DocumentMetadataRepositoryPort(Protocol):
    """Detailed class documentation for `DocumentMetadataRepositoryPort`.
    
    This component belongs to `src/document_analyzer_api/domain/ports/document_metadata_repository.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    async def upsert(self, document: DocumentMetadata) -> None:
        """Detailed asynchronous function documentation for `upsert`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/document_metadata_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                document: Input parameter for `upsert`.
        
            Returns:
                Value defined by `upsert` contract and consumed by downstream callers.
        """
        ...

    async def list_paginated(self, offset: int, limit: int) -> tuple[list[DocumentMetadata], int]:
        """Detailed asynchronous function documentation for `list_paginated`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/document_metadata_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Collects and returns a paginated or aggregated list of entities.
        
            Args:
                offset: Input parameter for `list_paginated`.
                limit: Input parameter for `list_paginated`.
        
            Returns:
                Value defined by `list_paginated` contract and consumed by downstream callers.
        """
        ...

