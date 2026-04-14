"""Detailed module documentation for `src/document_analyzer_api/domain/ports/chunk_repository.py`.

File role:
- Located in the domain port layer.
- Defines logic and symbols for `chunk_repository.py` within Document Analyzer V1.

Purpose:
- Declares abstract contracts implemented by infrastructure adapters.

Exported symbols overview:
- Classes: ChunkRepositoryPort.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from typing import Protocol

from ..models.persistence import PersistedChunk


class ChunkRepositoryPort(Protocol):
    """Detailed class documentation for `ChunkRepositoryPort`.
    
    This component belongs to `src/document_analyzer_api/domain/ports/chunk_repository.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    async def stage_chunks(self, document_id: str, chunks: list[PersistedChunk], ttl_seconds: int) -> None:
        """Detailed asynchronous function documentation for `stage_chunks`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/chunk_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                document_id: Input parameter for `stage_chunks`.
                chunks: Input parameter for `stage_chunks`.
                ttl_seconds: Input parameter for `stage_chunks`.
        
            Returns:
                Value defined by `stage_chunks` contract and consumed by downstream callers.
        """
        ...

    async def commit_document(self, document_id: str) -> None:
        """Detailed asynchronous function documentation for `commit_document`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/chunk_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                document_id: Input parameter for `commit_document`.
        
            Returns:
                Value defined by `commit_document` contract and consumed by downstream callers.
        """
        ...

    async def rollback_document(self, document_id: str) -> None:
        """Detailed asynchronous function documentation for `rollback_document`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/chunk_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                document_id: Input parameter for `rollback_document`.
        
            Returns:
                Value defined by `rollback_document` contract and consumed by downstream callers.
        """
        ...

