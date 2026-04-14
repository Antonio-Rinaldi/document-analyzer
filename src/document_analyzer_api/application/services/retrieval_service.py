"""Module `src/document_analyzer_api/application/services/retrieval_service.py`.

This module belongs to the application service layer of Document Analyzer.

Purpose:
- Coordinates use-case workflows over domain ports and adapters.

Defined symbols:
- Classes: RetrievalService.
- Functions: _chunk_index_from_id.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from ...domain.models.retrieval import Citation, RetrievalMode, RetrievalRequest, RetrievalResult
from ...domain.ports.retrieval_backend import RetrievalBackendPort


class RetrievalService:
    """RetrievalService application service.
    
    This class is defined in `src/document_analyzer_api/application/services/retrieval_service.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(
        self,
        *,
        vector_backend: RetrievalBackendPort,
        graph_backend: RetrievalBackendPort,
        hybrid_backend: RetrievalBackendPort,
    ) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/retrieval_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                vector_backend: Input parameter accepted by `__init__`.
                graph_backend: Input parameter accepted by `__init__`.
                hybrid_backend: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._backends: dict[RetrievalMode, RetrievalBackendPort] = {
            RetrievalMode.vector: vector_backend,
            RetrievalMode.graph: graph_backend,
            RetrievalMode.hybrid: hybrid_backend,
        }

    async def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        """Asynchronous execution path for `retrieve`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/retrieval_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes retrieval strategy selection and returns ranked evidence chunks.
        
            Args:
                request: Incoming HTTP request carrying route/query/body/context data.
        
            Returns:
                A value compatible with `RetrievalResult`.
        """
        backend = self._backends[request.retrieval_mode]
        hits = await backend.retrieve(request)
        citations: list[Citation] = []

        if request.include_sources:
            citations = [
                Citation(
                    document_id=hit.document_id,
                    chunk_id=hit.chunk_id,
                    chunk_index=_chunk_index_from_id(hit.chunk_id),
                )
                for hit in hits
            ]

        return RetrievalResult(hits=hits, citations=citations)


def _chunk_index_from_id(chunk_id: str) -> int | None:
    """Synchronous execution path for `_chunk_index_from_id`.
    
    This callable is implemented in `src/document_analyzer_api/application/services/retrieval_service.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (int, isdigit, split) to satisfy the callable contract.
    
        Args:
            chunk_id: Input parameter accepted by `_chunk_index_from_id`.
    
        Returns:
            A value compatible with `int | None`.
    """
    if ":" not in chunk_id:
        return None
    maybe_index = chunk_id.split(":")[-1]
    return int(maybe_index) if maybe_index.isdigit() else None


