from ...domain.models.retrieval import RetrievalHit, RetrievalRequest
from ...domain.ports.retrieval_backend import RetrievalBackendPort


class HybridRetrievalBackend(RetrievalBackendPort):
    def __init__(self, vector_backend: RetrievalBackendPort, graph_backend: RetrievalBackendPort) -> None:
        self._vector = vector_backend
        self._graph = graph_backend

    async def retrieve(self, request: RetrievalRequest) -> list[RetrievalHit]:
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

