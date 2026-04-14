"""Detailed module documentation for `src/document_analyzer_api/application/services/document_summary_service.py`.

File role:
- Located in the application service layer.
- Defines logic and symbols for `document_summary_service.py` within Document Analyzer V1.

Purpose:
- Implements use-case orchestration across domain ports and infrastructure adapters.

Exported symbols overview:
- Classes: DocumentSummaryService.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

import uuid

from .document_query_service import DocumentQueryService
from ...domain.ports.document_creator import DocumentCreatorPort
from ...domain.ports.output_storage import OutputStoragePort


class DocumentSummaryService:
    """Detailed class documentation for `DocumentSummaryService`.
    
    This application service belongs to `src/document_analyzer_api/application/services/document_summary_service.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(
        self,
        query_service: DocumentQueryService,
        output_storage: OutputStoragePort,
        document_creator: DocumentCreatorPort,
    ) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_summary_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                query_service: Input parameter for `__init__`.
                output_storage: Input parameter for `__init__`.
                document_creator: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._query_service = query_service
        self._output_storage = output_storage
        self._document_creator = document_creator

    @property
    def supported_output_formats(self) -> tuple[str, ...]:
        """Detailed synchronous function documentation for `supported_output_formats`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_summary_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `supported_output_formats` contract and consumed by downstream callers.
        """
        return self._document_creator.supported_output_formats()

    async def create_summary(self, document_ids: list[str] | None, keywords: list[str], output_format: str) -> str:
        """Detailed asynchronous function documentation for `create_summary`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/document_summary_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Creates a new resource and returns identifiers or resulting payloads.
        
            Args:
                document_ids: Optional subset of document identifiers to scope the operation.
                keywords: Optional keyword list used by retrieval behavior.
                output_format: Input parameter for `create_summary`.
        
            Returns:
                Value defined by `create_summary` contract and consumed by downstream callers.
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

