"""Module `src/document_analyzer_api/infrastructure/retrieval/hybrid_retrieval_backend.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: HybridRetrievalBackend.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from ...domain.models.retrieval import RetrievalHit, RetrievalRequest
from ...domain.ports.retrieval_backend import RetrievalBackendPort


class HybridRetrievalBackend(RetrievalBackendPort):
    """HybridRetrievalBackend component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/retrieval/hybrid_retrieval_backend.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, vector_backend: RetrievalBackendPort, graph_backend: RetrievalBackendPort) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/hybrid_retrieval_backend.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                vector_backend: Input parameter accepted by `__init__`.
                graph_backend: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._vector = vector_backend
        self._graph = graph_backend

    async def retrieve(self, request: RetrievalRequest) -> list[RetrievalHit]:
        """Asynchronous execution path for `retrieve`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/hybrid_retrieval_backend.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes retrieval strategy selection and returns ranked evidence chunks.
        
            Args:
                request: Incoming HTTP request carrying route/query/body/context data.
        
            Returns:
                A value compatible with `list[RetrievalHit]`.
        """
        vector_hits = await self._vector.retrieve(request)
        graph_hits = await self._graph.retrieve(request)

        fused: dict[tuple[str, str], RetrievalHit] = {}
        for hit in vector_hits:
            fused[(hit.document_id, hit.chunk_id)] = RetrievalHit(
                document_id=hit.document_id,
                chunk_id=hit.chunk_id,
                content=hit.content,
                score=request.hybrid_alpha * hit.score,
                metadata={**hit.metadata},
            )

        for hit in graph_hits:
            key = (hit.document_id, hit.chunk_id)
            if key in fused:
                fused[key].score += (1.0 - request.hybrid_alpha) * hit.score
            else:
                fused[key] = RetrievalHit(
                    document_id=hit.document_id,
                    chunk_id=hit.chunk_id,
                    content=hit.content,
                    score=(1.0 - request.hybrid_alpha) * hit.score,
                    metadata={**hit.metadata},
                )

        result = sorted(fused.values(), key=lambda item: item.score, reverse=True)
        return result[: request.top_k]

