"""Module `src/document_analyzer_api/application/services/document_summary_service.py`.

This module belongs to the application service layer of Document Analyzer.

Purpose:
- Coordinates use-case workflows over domain ports and adapters.

Defined symbols:
- Classes: DocumentSummaryService.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import uuid

from ...domain.models.retrieval import KeywordsMode, RetrievalMode, RetrievalRequest
from ...domain.ports.document_creator import DocumentCreatorPort
from ...domain.ports.output_storage import OutputStoragePort
from ...domain.ports.text_generation_client import TextGenerationClientPort
from .retrieval_service import RetrievalService


INSUFFICIENT_EVIDENCE_MESSAGE = "I cannot find enough support in selected documents."


class DocumentSummaryService:
    """DocumentSummaryService application service.
    
    This class is defined in `src/document_analyzer_api/application/services/document_summary_service.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(
        self,
        retrieval_service: RetrievalService,
        text_generation_client: TextGenerationClientPort,
        output_storage: OutputStoragePort,
        document_creator: DocumentCreatorPort,
    ) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_summary_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                retrieval_service: Input parameter accepted by `__init__`.
                text_generation_client: Input parameter accepted by `__init__`.
                output_storage: Input parameter accepted by `__init__`.
                document_creator: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._retrieval_service = retrieval_service
        self._text_generation_client = text_generation_client
        self._output_storage = output_storage
        self._document_creator = document_creator

    @property
    def supported_output_formats(self) -> tuple[str, ...]:
        """Synchronous execution path for `supported_output_formats`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_summary_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (supported_output_formats) to satisfy the callable contract.
        
            Args:
                None.
        
            Returns:
                A value compatible with `tuple[str, ...]`.
        """
        return self._document_creator.supported_output_formats()

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
        output_format: str,
    ) -> str:
        """Asynchronous execution path for `create_summary`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_summary_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Creates a resource and returns identifiers or materialized result payloads.
        
            Args:
                document_ids: Optional subset of documents used to scope the operation.
                keywords: Optional keyword list used for retrieval metadata/filtering/boosting.
                keywords_mode: Keyword strategy selector (`metadata_only`, `filter`, `rank_boost`).
                retrieval_mode: Retrieval backend mode (`vector`, `graph`, or `hybrid`).
                top_k: Maximum number of retrieval hits retained for context assembly.
                min_score: Minimum score threshold used to discard low-confidence hits.
                hybrid_alpha: Fusion weight for hybrid retrieval blending.
                graph_max_hops: Maximum traversal depth used by graph retrieval mode.
                summary_word_count: Optional target length guidance (in words) for summary generation.
                output_format: Input parameter accepted by `create_summary`.
        
            Returns:
                A value compatible with `str`.
        """
        summary_query = self._build_summary_query(keywords)
        retrieval_request = RetrievalRequest(
            query=summary_query,
            retrieval_mode=RetrievalMode(retrieval_mode),
            document_ids=document_ids,
            keywords=keywords,
            keywords_mode=KeywordsMode(keywords_mode),
            top_k=top_k,
            min_score=min_score,
            hybrid_alpha=hybrid_alpha,
            graph_max_hops=graph_max_hops,
            include_sources=False,
        )
        result = await self._retrieval_service.retrieve(retrieval_request)
        summary_text = INSUFFICIENT_EVIDENCE_MESSAGE
        if result.hits:
            summary_prompt = self._build_summary_prompt(keywords, summary_word_count)
            summary_text = await self._text_generation_client.generate_answer(
                question=summary_prompt,
                context_chunks=[hit.content for hit in result.hits],
            )

        stem = f"summary-{uuid.uuid4().hex}"
        created = await self._document_creator.create(
            summary_text=summary_text,
            output_format=output_format,
            filename_stem=stem,
        )
        content_type = "text/plain" if created.filename.endswith(".txt") else "text/markdown"
        return await self._output_storage.write_output(
            filename=created.filename,
            content=created.content,
            content_type=content_type,
        )

    @staticmethod
    def _build_summary_query(keywords: list[str]) -> str:
        """Build retrieval query text for summary evidence discovery."""
        if keywords:
            return " ".join(keywords)
        return "Provide a complete factual summary of the selected documents."

    @staticmethod
    def _build_summary_prompt(keywords: list[str], summary_word_count: int | None) -> str:
        """Build a neutral summary instruction consumed by text-generation adapters."""
        focus = f" Focus on: {', '.join(keywords)}." if keywords else ""
        length_instruction = (
            f" Target length: approximately {summary_word_count} words."
            if summary_word_count is not None
            else ""
        )
        return (
            "Create an encyclopedic summary of the selected documents. "
            "Cover major plot beats, character roles, and chronological progression with neutral tone."
            f"{focus}{length_instruction}"
        )

