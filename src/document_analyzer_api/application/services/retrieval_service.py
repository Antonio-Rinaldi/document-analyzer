"""Detailed module documentation for `src/document_analyzer_api/application/services/retrieval_service.py`.

File role:
- Located in the application service layer.
- Defines logic and symbols for `retrieval_service.py` within Document Analyzer V1.

Purpose:
- Implements use-case orchestration across domain ports and infrastructure adapters.

Exported symbols overview:
- Classes: RetrievalService.
- Functions: _chunk_index_from_id.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from ...domain.models.retrieval import Citation, RetrievalMode, RetrievalRequest, RetrievalResult
from ...domain.ports.retrieval_backend import RetrievalBackendPort


class RetrievalService:
    """Detailed class documentation for `RetrievalService`.
    
    This application service belongs to `src/document_analyzer_api/application/services/retrieval_service.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(
        self,
        *,
        vector_backend: RetrievalBackendPort,
        graph_backend: RetrievalBackendPort,
        hybrid_backend: RetrievalBackendPort,
    ) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/retrieval_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                vector_backend: Input parameter for `__init__`.
                graph_backend: Input parameter for `__init__`.
                hybrid_backend: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._backends: dict[RetrievalMode, RetrievalBackendPort] = {
            RetrievalMode.vector: vector_backend,
            RetrievalMode.graph: graph_backend,
            RetrievalMode.hybrid: hybrid_backend,
        }

    async def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        """Detailed asynchronous function documentation for `retrieve`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/retrieval_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes retrieval strategy selection and returns matching evidence chunks.
        
            Args:
                request: Incoming request object carrying path/query/body/context information.
        
            Returns:
                Value defined by `retrieve` contract and consumed by downstream callers.
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
    """Detailed synchronous function documentation for `_chunk_index_from_id`.
    
    This callable is implemented in `src/document_analyzer_api/application/services/retrieval_service.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            chunk_id: Input parameter for `_chunk_index_from_id`.
    
        Returns:
            Value defined by `_chunk_index_from_id` contract and consumed by downstream callers.
    """
    if ":" not in chunk_id:
        return None
    maybe_index = chunk_id.split(":")[-1]
    return int(maybe_index) if maybe_index.isdigit() else None


