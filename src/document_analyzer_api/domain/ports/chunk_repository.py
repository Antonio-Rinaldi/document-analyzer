"""Module `src/document_analyzer_api/domain/ports/chunk_repository.py`.

This module belongs to the domain abstraction layer of Document Analyzer.

Purpose:
- Declares protocol contracts implemented by infrastructure adapters.

Defined symbols:
- Classes: ChunkRepositoryPort.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from typing import Protocol

from ..models.persistence import PersistedChunk


class ChunkRepositoryPort(Protocol):
    """ChunkRepositoryPort component.
    
    This class is defined in `src/document_analyzer_api/domain/ports/chunk_repository.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    async def stage_chunks(self, document_id: str, chunks: list[PersistedChunk], ttl_seconds: int) -> None:
        """Asynchronous execution path for `stage_chunks`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/chunk_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                document_id: Input parameter accepted by `stage_chunks`.
                chunks: Input parameter accepted by `stage_chunks`.
                ttl_seconds: Input parameter accepted by `stage_chunks`.
        
            Returns:
                A value compatible with `None`.
        """
        ...

    async def commit_document(self, document_id: str) -> None:
        """Asynchronous execution path for `commit_document`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/chunk_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                document_id: Input parameter accepted by `commit_document`.
        
            Returns:
                A value compatible with `None`.
        """
        ...

    async def rollback_document(self, document_id: str) -> None:
        """Asynchronous execution path for `rollback_document`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/chunk_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                document_id: Input parameter accepted by `rollback_document`.
        
            Returns:
                A value compatible with `None`.
        """
        ...

