"""Detailed module documentation for `src/document_analyzer_api/application/services/document_generation_service.py`.

File role:
- Located in the application service layer.
- Defines logic and symbols for `document_generation_service.py` within Document Analyzer V1.

Purpose:
- Implements use-case orchestration across domain ports and infrastructure adapters.

Exported symbols overview:
- Classes: DocumentGenerationService.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from ...domain.models.retrieval import KeywordsMode, RetrievalMode, RetrievalRequest
from ...domain.ports.text_generation_client import TextGenerationClientPort
from .retrieval_service import RetrievalService


INSUFFICIENT_EVIDENCE_MESSAGE = "I cannot find enough support in selected documents."


class DocumentGenerationService:
    """Detailed class documentation for `DocumentGenerationService`.
    
    This application service belongs to `src/document_analyzer_api/application/services/document_generation_service.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, retrieval_service: RetrievalService, text_generation_client: TextGenerationClientPort) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_generation_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                retrieval_service: Input parameter for `__init__`.
                text_generation_client: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
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
        """Detailed asynchronous function documentation for `generate`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_generation_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Generates derived output from retrieved context and provided options.
        
            Args:
                question: User question or prompt text to process.
                document_ids: Optional subset of document identifiers to scope the operation.
                keywords: Optional keyword list used by retrieval behavior.
                keywords_mode: Retrieval keyword strategy selector.
                retrieval_mode: Retrieval backend mode (`vector`, `graph`, or `hybrid`).
                top_k: Maximum number of retrieved items considered in downstream steps.
                min_score: Minimum score threshold used to accept retrieval hits.
                hybrid_alpha: Fusion weight used when hybrid retrieval mode is selected.
                include_sources: Flag controlling citation/source emission in responses.
        
            Returns:
                Value defined by `generate` contract and consumed by downstream callers.
        """
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

