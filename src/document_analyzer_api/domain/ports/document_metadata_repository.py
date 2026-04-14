"""Module `src/document_analyzer_api/domain/ports/document_metadata_repository.py`.

This module belongs to the domain abstraction layer of Document Analyzer.

Purpose:
- Declares protocol contracts implemented by infrastructure adapters.

Defined symbols:
- Classes: DocumentMetadataRepositoryPort.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from typing import Protocol

from ..models.persistence import DocumentMetadata


class DocumentMetadataRepositoryPort(Protocol):
    """DocumentMetadataRepositoryPort component.
    
    This class is defined in `src/document_analyzer_api/domain/ports/document_metadata_repository.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    async def upsert(self, document: DocumentMetadata) -> None:
        """Asynchronous execution path for `upsert`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/document_metadata_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                document: Input parameter accepted by `upsert`.
        
            Returns:
                A value compatible with `None`.
        """
        ...

    async def list_paginated(self, offset: int, limit: int) -> tuple[list[DocumentMetadata], int]:
        """Asynchronous execution path for `list_paginated`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/document_metadata_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Collects and returns a list or paginated subset of entities.
        
            Args:
                offset: Input parameter accepted by `list_paginated`.
                limit: Input parameter accepted by `list_paginated`.
        
            Returns:
                A value compatible with `tuple[list[DocumentMetadata], int]`.
        """
        ...

