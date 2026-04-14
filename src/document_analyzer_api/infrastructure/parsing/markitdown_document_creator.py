from __future__ import annotations

from ...domain.ports.document_creator import CreatedDocument, DocumentCreatorPort
from ..markitdown.capabilities import SUPPORTED_OUTPUT_FORMATS


class MarkItDownDocumentCreator(DocumentCreatorPort):
    def supported_output_formats(self) -> tuple[str, ...]:
        return SUPPORTED_OUTPUT_FORMATS

    async def create(self, *, summary_text: str, output_format: str, filename_stem: str) -> CreatedDocument:
        normalized = output_format.strip().lower()
        if normalized not in self.supported_output_formats():
            allowed = ", ".join(self.supported_output_formats())
            raise ValueError(f"Unsupported summary outputFormat '{output_format}'. Supported values: {allowed}")

        if normalized in {"md", "markdown"}:
            return CreatedDocument(filename=f"{filename_stem}.md", content=summary_text.encode("utf-8"))

        plain = self._to_plain_text(summary_text)
        return CreatedDocument(filename=f"{filename_stem}.txt", content=plain.encode("utf-8"))

    def _to_plain_text(self, markdown_text: str) -> str:
        return "\n".join(line.lstrip("#").strip() for line in markdown_text.splitlines()).strip()
