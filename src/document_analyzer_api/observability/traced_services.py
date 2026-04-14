"""Detailed module documentation for `src/document_analyzer_api/observability/traced_services.py`.

File role:
- Located in the observability layer.
- Defines logic and symbols for `traced_services.py` within Document Analyzer V1.

Purpose:
- Supports a focused concern in the Document Analyzer codebase.

Exported symbols overview:
- Classes: TracedDocumentProcessingPipelineService, TracedRetrievalService, TracedDocumentGenerationService, TracedChatService.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from __future__ import annotations

from ..application.services.chat_service import ChatService
from ..application.services.document_generation_service import DocumentGenerationService
from ..application.services.document_processing_pipeline_service import DocumentProcessingPipelineService
from ..application.services.retrieval_service import RetrievalService
from ..domain.models.chunking import ChunkingConfig
from ..domain.models.retrieval import RetrievalRequest, RetrievalResult
from .tracing import traced_async


class TracedDocumentProcessingPipelineService(DocumentProcessingPipelineService):
    """Detailed class documentation for `TracedDocumentProcessingPipelineService`.
    
    This application service belongs to `src/document_analyzer_api/observability/traced_services.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """

    def __init__(self, inner: DocumentProcessingPipelineService) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                inner: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._inner = inner

    @traced_async(
        "document.process",
        attribute_builder=lambda self, file_name, content, chunking_config: {
            "document_name": file_name,
            "chunking_strategy": chunking_config.strategy.value,
        },
    )
    async def process(self, file_name: str, content: bytes, chunking_config: ChunkingConfig) -> str:
        """Detailed asynchronous function documentation for `process`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                file_name: Input parameter for `process`.
                content: Raw payload bytes or text handled by the callable.
                chunking_config: Input parameter for `process`.
        
            Returns:
                Value defined by `process` contract and consumed by downstream callers.
        """
        return await self._inner.process(file_name, content, chunking_config)


class TracedRetrievalService(RetrievalService):
    """Detailed class documentation for `TracedRetrievalService`.
    
    This application service belongs to `src/document_analyzer_api/observability/traced_services.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """

    def __init__(self, inner: RetrievalService) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                inner: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._inner = inner

    @traced_async(
        "document.retrieve",
        attribute_builder=lambda self, request: {
            "retrieval_mode": request.retrieval_mode.value,
            "top_k": request.top_k,
        },
    )
    async def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        """Detailed asynchronous function documentation for `retrieve`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes retrieval strategy selection and returns matching evidence chunks.
        
            Args:
                request: Incoming request object carrying path/query/body/context information.
        
            Returns:
                Value defined by `retrieve` contract and consumed by downstream callers.
        """
        return await self._inner.retrieve(request)


class TracedDocumentGenerationService(DocumentGenerationService):
    """Detailed class documentation for `TracedDocumentGenerationService`.
    
    This application service belongs to `src/document_analyzer_api/observability/traced_services.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """

    def __init__(self, inner: DocumentGenerationService) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                inner: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._inner = inner

    @traced_async(
        "document.generate",
        attribute_builder=lambda self, question, document_ids, keywords, keywords_mode, retrieval_mode, top_k, min_score, hybrid_alpha, include_sources: {
            "retrieval_mode": retrieval_mode,
            "include_sources": include_sources,
        },
    )
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
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to the module workflow
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
        return await self._inner.generate(
            question=question,
            document_ids=document_ids,
            keywords=keywords,
            keywords_mode=keywords_mode,
            retrieval_mode=retrieval_mode,
            top_k=top_k,
            min_score=min_score,
            hybrid_alpha=hybrid_alpha,
            include_sources=include_sources,
        )


class TracedChatService(ChatService):
    """Detailed class documentation for `TracedChatService`.
    
    This application service belongs to `src/document_analyzer_api/observability/traced_services.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """

    def __init__(self, inner: ChatService) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                inner: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._inner = inner

    async def create_session(self) -> str:
        """Detailed asynchronous function documentation for `create_session`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Creates a new resource and returns identifiers or resulting payloads.
        
            Args:
                None.
        
            Returns:
                Value defined by `create_session` contract and consumed by downstream callers.
        """
        return await self._inner.create_session()

    async def delete_session(self, session_id: str) -> bool:
        """Detailed asynchronous function documentation for `delete_session`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Deletes a resource and reports whether deletion succeeded.
        
            Args:
                session_id: Server-side chat session identifier.
        
            Returns:
                Value defined by `delete_session` contract and consumed by downstream callers.
        """
        return await self._inner.delete_session(session_id)

    @traced_async(
        "document.chat",
        attribute_builder=lambda self, session_id, question, document_ids, keywords, keywords_mode, retrieval_mode, top_k, min_score, hybrid_alpha, include_sources, compact_context: {
            "session_id": session_id,
        },
    )
    async def chat(
        self,
        *,
        session_id: str,
        question: str,
        document_ids: list[str] | None,
        keywords: list[str],
        keywords_mode: str,
        retrieval_mode: str,
        top_k: int,
        min_score: float,
        hybrid_alpha: float,
        include_sources: bool,
        compact_context: bool,
    ) -> tuple[str, list[dict]]:
        """Detailed asynchronous function documentation for `chat`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes stateful chat logic using persisted session context.
        
            Args:
                session_id: Server-side chat session identifier.
                question: User question or prompt text to process.
                document_ids: Optional subset of document identifiers to scope the operation.
                keywords: Optional keyword list used by retrieval behavior.
                keywords_mode: Retrieval keyword strategy selector.
                retrieval_mode: Retrieval backend mode (`vector`, `graph`, or `hybrid`).
                top_k: Maximum number of retrieved items considered in downstream steps.
                min_score: Minimum score threshold used to accept retrieval hits.
                hybrid_alpha: Fusion weight used when hybrid retrieval mode is selected.
                include_sources: Flag controlling citation/source emission in responses.
                compact_context: Flag requesting immediate chat context compaction.
        
            Returns:
                Value defined by `chat` contract and consumed by downstream callers.
        """
        return await self._inner.chat(
            session_id=session_id,
            question=question,
            document_ids=document_ids,
            keywords=keywords,
            keywords_mode=keywords_mode,
            retrieval_mode=retrieval_mode,
            top_k=top_k,
            min_score=min_score,
            hybrid_alpha=hybrid_alpha,
            include_sources=include_sources,
            compact_context=compact_context,
        )




