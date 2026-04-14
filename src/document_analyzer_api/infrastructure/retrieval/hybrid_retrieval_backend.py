"""Detailed module documentation for `src/document_analyzer_api/infrastructure/retrieval/hybrid_retrieval_backend.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `hybrid_retrieval_backend.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: HybridRetrievalBackend.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from ...domain.models.retrieval import RetrievalHit, RetrievalRequest
from ...domain.ports.retrieval_backend import RetrievalBackendPort


class HybridRetrievalBackend(RetrievalBackendPort):
    """Detailed class documentation for `HybridRetrievalBackend`.
    
    This component belongs to `src/document_analyzer_api/infrastructure/retrieval/hybrid_retrieval_backend.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, vector_backend: RetrievalBackendPort, graph_backend: RetrievalBackendPort) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/hybrid_retrieval_backend.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                vector_backend: Input parameter for `__init__`.
                graph_backend: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._vector = vector_backend
        self._graph = graph_backend

    async def retrieve(self, request: RetrievalRequest) -> list[RetrievalHit]:
        """Detailed asynchronous function documentation for `retrieve`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/retrieval/hybrid_retrieval_backend.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes retrieval strategy selection and returns matching evidence chunks.
        
            Args:
                request: Incoming request object carrying path/query/body/context information.
        
            Returns:
                Value defined by `retrieve` contract and consumed by downstream callers.
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

