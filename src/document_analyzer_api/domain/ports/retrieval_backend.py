"""Module `src/document_analyzer_api/domain/ports/retrieval_backend.py`.

This module belongs to the domain abstraction layer of Document Analyzer.

Purpose:
- Declares protocol contracts implemented by infrastructure adapters.

Defined symbols:
- Classes: RetrievalBackendPort.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from typing import Protocol

from ..models.retrieval import RetrievalHit, RetrievalRequest


class RetrievalBackendPort(Protocol):
    """RetrievalBackendPort component.
    
    This class is defined in `src/document_analyzer_api/domain/ports/retrieval_backend.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    async def retrieve(self, request: RetrievalRequest) -> list[RetrievalHit]:
        """Asynchronous execution path for `retrieve`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/retrieval_backend.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes retrieval strategy selection and returns ranked evidence chunks.
        
            Args:
                request: Incoming HTTP request carrying route/query/body/context data.
        
            Returns:
                A value compatible with `list[RetrievalHit]`.
        """
        ...

