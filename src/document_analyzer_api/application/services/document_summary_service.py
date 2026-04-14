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

from .document_query_service import DocumentQueryService
from ...domain.ports.document_creator import DocumentCreatorPort
from ...domain.ports.output_storage import OutputStoragePort


class DocumentSummaryService:
    """DocumentSummaryService application service.
    
    This class is defined in `src/document_analyzer_api/application/services/document_summary_service.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(
        self,
        query_service: DocumentQueryService,
        output_storage: OutputStoragePort,
        document_creator: DocumentCreatorPort,
    ) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_summary_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                query_service: Input parameter accepted by `__init__`.
                output_storage: Input parameter accepted by `__init__`.
                document_creator: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._query_service = query_service
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

    async def create_summary(self, document_ids: list[str] | None, keywords: list[str], output_format: str) -> str:
        """Asynchronous execution path for `create_summary`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_summary_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Creates a resource and returns identifiers or materialized result payloads.
        
            Args:
                document_ids: Optional subset of documents used to scope the operation.
                keywords: Optional keyword list used for retrieval metadata/filtering/boosting.
                output_format: Input parameter accepted by `create_summary`.
        
            Returns:
                A value compatible with `str`.
        """
        items, _ = await self._query_service.list_documents(offset=0, limit=10000)
        selected = items
        if document_ids is not None:
            selected = [item for item in items if item.id in document_ids]

        base_text = "\n\n".join(item.description for item in selected if item.description)
        if not base_text:
            base_text = "No document content available for summary."
        if keywords:
            base_text += f"\n\nKeywords focus: {', '.join(keywords)}"

        stem = f"summary-{uuid.uuid4().hex}"
        created = await self._document_creator.create(
            summary_text=base_text,
            output_format=output_format,
            filename_stem=stem,
        )
        content_type = "text/plain" if created.filename.endswith(".txt") else "text/markdown"
        return await self._output_storage.write_output(
            filename=created.filename,
            content=created.content,
            content_type=content_type,
        )

