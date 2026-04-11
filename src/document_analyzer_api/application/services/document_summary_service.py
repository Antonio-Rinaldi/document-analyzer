import uuid

from .document_query_service import DocumentQueryService
from ...domain.ports.output_storage import OutputStoragePort


class DocumentSummaryService:
    def __init__(self, query_service: DocumentQueryService, output_storage: OutputStoragePort) -> None:
        self._query_service = query_service
        self._output_storage = output_storage

    async def create_summary(self, document_ids: list[str] | None, keywords: list[str]) -> str:
        items, _ = await self._query_service.list_documents(offset=0, limit=10000)
        selected = items
        if document_ids is not None:
            selected = [item for item in items if item.id in document_ids]

        base_text = "\n\n".join(item.description for item in selected if item.description)
        if not base_text:
            base_text = "No document content available for summary."
        if keywords:
            base_text += f"\n\nKeywords focus: {', '.join(keywords)}"

        filename = f"summary-{uuid.uuid4().hex}.epub"
        return await self._output_storage.write_output(filename=filename, content=base_text)

