from ...domain.models.retrieval import Citation, RetrievalMode, RetrievalRequest, RetrievalResult
from ...observability.tracing import set_span_attribute, start_span
from ...domain.ports.retrieval_backend import RetrievalBackendPort


class RetrievalService:
    def __init__(
        self,
        *,
        vector_backend: RetrievalBackendPort,
        graph_backend: RetrievalBackendPort,
        hybrid_backend: RetrievalBackendPort,
    ) -> None:
        self._backends: dict[RetrievalMode, RetrievalBackendPort] = {
            RetrievalMode.vector: vector_backend,
            RetrievalMode.graph: graph_backend,
            RetrievalMode.hybrid: hybrid_backend,
        }

    async def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        with start_span("document.retrieve"):
            set_span_attribute("retrieval_mode", request.retrieval_mode.value)
            set_span_attribute("top_k", request.top_k)
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
    if ":" not in chunk_id:
        return None
    maybe_index = chunk_id.split(":")[-1]
    return int(maybe_index) if maybe_index.isdigit() else None


