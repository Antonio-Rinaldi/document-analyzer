"""Module `src/document_analyzer_api/observability/traced_services.py`.

This module belongs to the observability layer of Document Analyzer.

Purpose:
- Implements metrics, tracing, and request-level telemetry support.

Defined symbols:
- Classes: TracedDocumentProcessingPipelineService, TracedRetrievalService, TracedDocumentGenerationService, TracedChatService.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from __future__ import annotations

from ..application.services.audio_service import AudioService
from ..application.services.chat_service import ChatService
from ..application.services.document_ingestion_service import DocumentIngestionService, IngestionResult
from ..application.services.document_query_service import DocumentQueryService
from ..application.services.document_summary_service import DocumentSummaryService
from ..application.services.document_generation_service import DocumentGenerationService
from ..application.services.document_processing_pipeline_service import DocumentProcessingPipelineService
from ..application.services.image_service import ImageService
from ..application.services.retrieval_service import RetrievalService
from ..domain.models.chunking import ChunkingConfig
from ..domain.models.retrieval import RetrievalRequest, RetrievalResult
from ..domain.ports.document_storage import UploadedFileData
from .metrics import metered_async
from .tracing import traced_async


class TracedDocumentProcessingPipelineService(DocumentProcessingPipelineService):
    """TracedDocumentProcessingPipelineService application service.
    
    This class is defined in `src/document_analyzer_api/observability/traced_services.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """

    def __init__(self, inner: DocumentProcessingPipelineService) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                inner: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._inner = inner

    @traced_async(
        "document.process",
        attribute_builder=lambda self, file_name, content, chunking_config: {
            "document_name": file_name,
            "chunking_strategy": chunking_config.strategy.value,
        },
    )
    @metered_async("service.document_processing_pipeline", "process")
    async def process(self, file_name: str, content: bytes, chunking_config: ChunkingConfig) -> str:
        """Asynchronous execution path for `process`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (process, traced_async) to satisfy the callable contract.
        
            Args:
                file_name: Input parameter accepted by `process`.
                content: Raw payload bytes/text processed or transformed by this callable.
                chunking_config: Input parameter accepted by `process`.
        
            Returns:
                A value compatible with `str`.
        """
        return await self._inner.process(file_name, content, chunking_config)


class TracedRetrievalService(RetrievalService):
    """TracedRetrievalService application service.
    
    This class is defined in `src/document_analyzer_api/observability/traced_services.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """

    def __init__(self, inner: RetrievalService) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                inner: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._inner = inner

    @traced_async(
        "document.retrieve",
        attribute_builder=lambda self, request: {
            "retrieval_mode": request.retrieval_mode.value,
            "top_k": request.top_k,
        },
    )
    @metered_async("service.retrieval", "retrieve")
    async def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        """Asynchronous execution path for `retrieve`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes retrieval strategy selection and returns ranked evidence chunks.
        
            Args:
                request: Incoming HTTP request carrying route/query/body/context data.
        
            Returns:
                A value compatible with `RetrievalResult`.
        """
        return await self._inner.retrieve(request)


class TracedDocumentGenerationService(DocumentGenerationService):
    """TracedDocumentGenerationService application service.
    
    This class is defined in `src/document_analyzer_api/observability/traced_services.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """

    def __init__(self, inner: DocumentGenerationService) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                inner: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._inner = inner

    @traced_async(
        "document.generate",
        attribute_builder=lambda self, question, document_ids, keywords, keywords_mode, retrieval_mode, top_k, min_score, hybrid_alpha, include_sources, graph_max_hops=2: {
            "retrieval_mode": retrieval_mode,
            "include_sources": include_sources,
            "graph.max_hops": graph_max_hops,
        },
    )
    @metered_async("service.generation", "generate")
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
        graph_max_hops: int = 2,
    ) -> tuple[str, list[dict]]:
        """Asynchronous execution path for `generate`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Generates derived output from context, prompts, and generation options.
        
            Args:
                question: User prompt processed by retrieval and generation workflows.
                document_ids: Optional subset of documents used to scope the operation.
                keywords: Optional keyword list used for retrieval metadata/filtering/boosting.
                keywords_mode: Keyword strategy selector (`metadata_only`, `filter`, `rank_boost`).
                retrieval_mode: Retrieval backend mode (`vector`, `graph`, or `hybrid`).
                top_k: Maximum number of retrieval hits retained for context assembly.
                min_score: Minimum score threshold used to discard low-confidence hits.
                hybrid_alpha: Fusion weight for hybrid retrieval blending.
                include_sources: Flag controlling citation extraction in response payloads.
                graph_max_hops: Maximum traversal depth used by graph retrieval mode.
        
            Returns:
                A value compatible with `tuple[str, list[dict]]`.
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
            graph_max_hops=graph_max_hops,
        )


class TracedChatService(ChatService):
    """TracedChatService application service.
    
    This class is defined in `src/document_analyzer_api/observability/traced_services.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """

    def __init__(self, inner: ChatService) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                inner: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._inner = inner

    @traced_async("document.chat.session.create")
    @metered_async("service.chat", "create_session")
    async def create_session(self) -> str:
        """Asynchronous execution path for `create_session`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Creates a resource and returns identifiers or materialized result payloads.
        
            Args:
                None.
        
            Returns:
                A value compatible with `str`.
        """
        return await self._inner.create_session()

    @traced_async("document.chat.session.delete", attribute_builder=lambda self, session_id: {"session_id": session_id})
    @metered_async("service.chat", "delete_session")
    async def delete_session(self, session_id: str) -> bool:
        """Asynchronous execution path for `delete_session`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Deletes a target resource and reports outcome deterministically.
        
            Args:
                session_id: Server-side chat session identifier.
        
            Returns:
                A value compatible with `bool`.
        """
        return await self._inner.delete_session(session_id)

    @traced_async(
        "document.chat",
        attribute_builder=lambda self, session_id, question, document_ids, keywords, keywords_mode, retrieval_mode, top_k, min_score, hybrid_alpha, include_sources, graph_max_hops, compact_context: {
            "session_id": session_id,
            "graph.max_hops": graph_max_hops,
        },
    )
    @metered_async("service.chat", "chat")
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
        graph_max_hops: int,
        compact_context: bool,
    ) -> tuple[str, list[dict]]:
        """Asynchronous execution path for `chat`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Runs stateful chat logic with persisted context and new user input.
        
            Args:
                session_id: Server-side chat session identifier.
                question: User prompt processed by retrieval and generation workflows.
                document_ids: Optional subset of documents used to scope the operation.
                keywords: Optional keyword list used for retrieval metadata/filtering/boosting.
                keywords_mode: Keyword strategy selector (`metadata_only`, `filter`, `rank_boost`).
                retrieval_mode: Retrieval backend mode (`vector`, `graph`, or `hybrid`).
                top_k: Maximum number of retrieval hits retained for context assembly.
                min_score: Minimum score threshold used to discard low-confidence hits.
                hybrid_alpha: Fusion weight for hybrid retrieval blending.
                include_sources: Flag controlling citation extraction in response payloads.
                graph_max_hops: Maximum traversal depth used by graph retrieval mode.
                compact_context: Flag requesting immediate context compaction in chat flows.
        
            Returns:
                A value compatible with `tuple[str, list[dict]]`.
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
            graph_max_hops=graph_max_hops,
            compact_context=compact_context,
        )


class TracedDocumentIngestionService(DocumentIngestionService):
    """TracedDocumentIngestionService application service.
    
    This class is defined in `src/document_analyzer_api/observability/traced_services.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """

    def __init__(self, inner: DocumentIngestionService) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                inner: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._inner = inner

    @property
    def supported_extensions(self) -> tuple[str, ...]:
        return self._inner.supported_extensions

    @traced_async(
        "document.ingest",
        attribute_builder=lambda self, files, chunking_config: {
            "files.count": len(files),
            "chunking.strategy": chunking_config.strategy.value,
        },
    )
    @metered_async("service.ingestion", "ingest_files")
    async def ingest_files(self, files: list[UploadedFileData], chunking_config: ChunkingConfig) -> list[IngestionResult]:
        return await self._inner.ingest_files(files, chunking_config)


class TracedDocumentQueryService(DocumentQueryService):
    """TracedDocumentQueryService application service.
    
    This class is defined in `src/document_analyzer_api/observability/traced_services.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """

    def __init__(self, inner: DocumentQueryService) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                inner: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._inner = inner

    @traced_async(
        "document.query.list",
        attribute_builder=lambda self, offset, limit: {"pagination.offset": offset, "pagination.limit": limit},
    )
    @metered_async("service.document_query", "list_documents")
    async def list_documents(self, offset: int, limit: int):
        return await self._inner.list_documents(offset=offset, limit=limit)


class TracedDocumentSummaryService(DocumentSummaryService):
    """TracedDocumentSummaryService application service.
    
    This class is defined in `src/document_analyzer_api/observability/traced_services.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """

    def __init__(self, inner: DocumentSummaryService) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                inner: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._inner = inner

    @property
    def supported_output_formats(self) -> tuple[str, ...]:
        return self._inner.supported_output_formats

    @traced_async(
        "document.summary.create",
        attribute_builder=lambda self, document_ids, keywords, keywords_mode, retrieval_mode, top_k, min_score, hybrid_alpha, graph_max_hops, summary_word_count, summary_prompt, output_format: {
            "documents.count": len(document_ids or []),
            "keywords.count": len(keywords),
            "retrieval.mode": retrieval_mode,
            "retrieval.top_k": top_k,
            "retrieval.min_score": min_score,
            "retrieval.hybrid_alpha": hybrid_alpha,
            "retrieval.graph_max_hops": graph_max_hops,
            "summary.word_count": summary_word_count or 0,
            "summary.has_custom_prompt": bool(summary_prompt),
            "output.format": output_format,
        },
    )
    @metered_async("service.document_summary", "create_summary")
    async def create_summary(
        self,
        *,
        document_ids: list[str] | None,
        keywords: list[str],
        keywords_mode: str,
        retrieval_mode: str,
        top_k: int,
        min_score: float,
        hybrid_alpha: float,
        graph_max_hops: int,
        summary_word_count: int | None,
        summary_prompt: str | None,
        output_format: str,
    ) -> tuple[str, str]:
        return await self._inner.create_summary(
            document_ids=document_ids,
            keywords=keywords,
            keywords_mode=keywords_mode,
            retrieval_mode=retrieval_mode,
            top_k=top_k,
            min_score=min_score,
            hybrid_alpha=hybrid_alpha,
            graph_max_hops=graph_max_hops,
            summary_word_count=summary_word_count,
            summary_prompt=summary_prompt,
            output_format=output_format,
        )


class TracedAudioService(AudioService):
    """TracedAudioService application service.
    
    This class is defined in `src/document_analyzer_api/observability/traced_services.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """

    def __init__(self, inner: AudioService) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                inner: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._inner = inner

    @traced_async(
        "document.audio.generate",
        attribute_builder=lambda self, question, document_ids, keywords, keywords_mode, retrieval_mode, top_k, min_score, hybrid_alpha, include_sources, graph_max_hops, audio_format: {
            "retrieval.mode": retrieval_mode,
            "audio.format": audio_format,
            "keywords.count": len(keywords),
            "graph.max_hops": graph_max_hops,
        },
    )
    @metered_async("service.audio", "generate_audio_answer")
    async def generate_audio_answer(
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
        graph_max_hops: int,
        audio_format: str,
    ) -> tuple[bytes, list[dict]]:
        return await self._inner.generate_audio_answer(
            question=question,
            document_ids=document_ids,
            keywords=keywords,
            keywords_mode=keywords_mode,
            retrieval_mode=retrieval_mode,
            top_k=top_k,
            min_score=min_score,
            hybrid_alpha=hybrid_alpha,
            include_sources=include_sources,
            graph_max_hops=graph_max_hops,
            audio_format=audio_format,
        )

    def render_audio(self, text: str, audio_format: str) -> bytes:
        return self._inner.render_audio(text=text, audio_format=audio_format)


class TracedImageService(ImageService):
    """TracedImageService application service.
    
    This class is defined in `src/document_analyzer_api/observability/traced_services.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """

    def __init__(self, inner: ImageService) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/observability/traced_services.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                inner: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._inner = inner

    @traced_async(
        "document.image.generate",
        attribute_builder=lambda self, question, document_ids, keywords, keywords_mode, retrieval_mode, top_k, min_score, hybrid_alpha, include_sources, graph_max_hops: {
            "retrieval.mode": retrieval_mode,
            "keywords.count": len(keywords),
            "graph.max_hops": graph_max_hops,
        },
    )
    @metered_async("service.image", "generate_image_answer")
    async def generate_image_answer(
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
        graph_max_hops: int,
    ) -> tuple[str, dict, list[dict]]:
        return await self._inner.generate_image_answer(
            question=question,
            document_ids=document_ids,
            keywords=keywords,
            keywords_mode=keywords_mode,
            retrieval_mode=retrieval_mode,
            top_k=top_k,
            min_score=min_score,
            hybrid_alpha=hybrid_alpha,
            include_sources=include_sources,
            graph_max_hops=graph_max_hops,
        )

    def render_image(self, text: str) -> dict:
        return self._inner.render_image(text)
