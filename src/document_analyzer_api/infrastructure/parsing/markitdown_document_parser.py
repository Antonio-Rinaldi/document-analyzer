from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path

from markitdown import MarkItDown

from ...domain.models.chunking import ParsedDocument, ParsedSection
from ...domain.ports.document_parser import DocumentParserPort
from ..markitdown.capabilities import discover_supported_input_extensions


class MarkItDownDocumentParser(DocumentParserPort):
    def __init__(self) -> None:
        self._markitdown = MarkItDown(enable_plugins=False)
        self._supported_extensions = discover_supported_input_extensions()

    def supported_extensions(self) -> tuple[str, ...]:
        return self._supported_extensions

    async def parse(self, document_name: str, content: bytes) -> ParsedDocument:
        extension = Path(document_name).suffix.lower()
        result = self._markitdown.convert_stream(BytesIO(content), file_extension=extension or None)
        text = (result.text_content or "").strip()
        if not text:
            text = "Empty document"

        sections = self._to_sections(document_name=document_name, text=text)
        return ParsedDocument(document_name=document_name, sections=sections)

    def _to_sections(self, *, document_name: str, text: str) -> list[ParsedSection]:
        heading_pattern = re.compile(r"^#{1,6}\s+.+$", re.MULTILINE)
        headings = list(heading_pattern.finditer(text))
        if not headings:
            return [ParsedSection(section_id="section-0", title=Path(document_name).name, text=text)]

        sections: list[ParsedSection] = []
        for index, match in enumerate(headings):
            start = match.start()
            end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
            raw_chunk = text[start:end].strip()
            title = match.group().lstrip("#").strip()
            sections.append(
                ParsedSection(
                    section_id=f"section-{index}",
                    title=title or f"Section {index + 1}",
                    text=raw_chunk,
                )
            )

        return sections

