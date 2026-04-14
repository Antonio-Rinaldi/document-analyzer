import uuid

from .document_query_service import DocumentQueryService
from ...domain.ports.document_creator import DocumentCreatorPort
from ...domain.ports.output_storage import OutputStoragePort


class DocumentSummaryService:
    def __init__(
        self,
        query_service: DocumentQueryService,
        output_storage: OutputStoragePort,
        document_creator: DocumentCreatorPort,
    ) -> None:
        self._query_service = query_service
        self._output_storage = output_storage
        self._document_creator = document_creator

    @property
    def supported_output_formats(self) -> tuple[str, ...]:
        return self._document_creator.supported_output_formats()

    async def create_summary(self, document_ids: list[str] | None, keywords: list[str], output_format: str) -> str:
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

