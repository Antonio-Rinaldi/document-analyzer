from ...domain.models.retrieval import KeywordsMode, RetrievalMode, RetrievalRequest
from ...domain.ports.text_generation_client import TextGenerationClientPort
from ...observability.tracing import set_span_attribute, start_span
from .retrieval_service import RetrievalService


INSUFFICIENT_EVIDENCE_MESSAGE = "I cannot find enough support in selected documents."


class DocumentGenerationService:
    def __init__(self, retrieval_service: RetrievalService, text_generation_client: TextGenerationClientPort) -> None:
        self._retrieval_service = retrieval_service
        self._text_generation_client = text_generation_client

    async def generate(
        self,
        *,
        question: str,
        document_ids: list[str] | None,
        keywords: list[str],
        keywords_mode: str,
        retrieval_mode: str,
        top_k: int,
        min_score: float,
        hybrid_alpha: float,
        include_sources: bool,
    ) -> tuple[str, list[dict]]:
        with start_span("document.generate"):
            set_span_attribute("retrieval_mode", retrieval_mode)
            set_span_attribute("include_sources", include_sources)
            request = RetrievalRequest(
                query=question,
                retrieval_mode=RetrievalMode(retrieval_mode),
                document_ids=document_ids,
                keywords=keywords,
                keywords_mode=KeywordsMode(keywords_mode),
                top_k=top_k,
                min_score=min_score,
                hybrid_alpha=hybrid_alpha,
                include_sources=include_sources,
            )
            result = await self._retrieval_service.retrieve(request)

            if not result.hits:
                return INSUFFICIENT_EVIDENCE_MESSAGE, []

            context_chunks = [hit.content for hit in result.hits]
            answer = await self._text_generation_client.generate_answer(question=question, context_chunks=context_chunks)
            citations = [
                {
                    "documentId": citation.document_id,
                    "chunkId": citation.chunk_id,
                    "chunkIndex": citation.chunk_index,
                }
                for citation in result.citations
            ]
            return answer, citations

