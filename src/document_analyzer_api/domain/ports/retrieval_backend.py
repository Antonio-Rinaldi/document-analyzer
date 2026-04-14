"""Detailed module documentation for `src/document_analyzer_api/domain/ports/retrieval_backend.py`.

File role:
- Located in the domain port layer.
- Defines logic and symbols for `retrieval_backend.py` within Document Analyzer V1.

Purpose:
- Declares abstract contracts implemented by infrastructure adapters.

Exported symbols overview:
- Classes: RetrievalBackendPort.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from typing import Protocol

from ..models.retrieval import RetrievalHit, RetrievalRequest


class RetrievalBackendPort(Protocol):
    """Detailed class documentation for `RetrievalBackendPort`.
    
    This component belongs to `src/document_analyzer_api/domain/ports/retrieval_backend.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    async def retrieve(self, request: RetrievalRequest) -> list[RetrievalHit]:
        """Detailed asynchronous function documentation for `retrieve`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/retrieval_backend.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes retrieval strategy selection and returns matching evidence chunks.
        
            Args:
                request: Incoming request object carrying path/query/body/context information.
        
            Returns:
                Value defined by `retrieve` contract and consumed by downstream callers.
        """
        ...

