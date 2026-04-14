"""Module `src/document_analyzer_api/infrastructure/parsing/markitdown_document_parser.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: MarkItDownDocumentParser.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path

from markitdown import MarkItDown

from ...domain.models.chunking import ParsedDocument, ParsedSection
from ...domain.ports.document_parser import DocumentParserPort
from ..markitdown.capabilities import discover_supported_input_extensions


class MarkItDownDocumentParser(DocumentParserPort):
    """MarkItDownDocumentParser component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/parsing/markitdown_document_parser.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/parsing/markitdown_document_parser.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (MarkItDown, discover_supported_input_extensions) to satisfy the callable contract.
        
            Args:
                None.
        
            Returns:
                A value compatible with `None`.
        """
        self._markitdown = MarkItDown(enable_plugins=False)
        self._supported_extensions = discover_supported_input_extensions()

    def supported_extensions(self) -> tuple[str, ...]:
        """Synchronous execution path for `supported_extensions`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/parsing/markitdown_document_parser.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                None.
        
            Returns:
                A value compatible with `tuple[str, ...]`.
        """
        return self._supported_extensions

    async def parse(self, document_name: str, content: bytes) -> ParsedDocument:
        """Asynchronous execution path for `parse`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/parsing/markitdown_document_parser.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Parses incoming payloads and converts them to structured internal objects.
        
            Args:
                document_name: Input parameter accepted by `parse`.
                content: Raw payload bytes/text processed or transformed by this callable.
        
            Returns:
                A value compatible with `ParsedDocument`.
        """
        extension = Path(document_name).suffix.lower()
        result = self._markitdown.convert_stream(BytesIO(content), file_extension=extension or None)
        text = (result.text_content or "").strip()
        if not text:
            text = "Empty document"

        sections = self._to_sections(document_name=document_name, text=text)
        return ParsedDocument(document_name=document_name, sections=sections)

    def _to_sections(self, *, document_name: str, text: str) -> list[ParsedSection]:
        """Synchronous execution path for `_to_sections`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/parsing/markitdown_document_parser.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (ParsedSection, Path, append, compile) to satisfy the callable contract.
        
            Args:
                document_name: Input parameter accepted by `_to_sections`.
                text: Input parameter accepted by `_to_sections`.
        
            Returns:
                A value compatible with `list[ParsedSection]`.
        """
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

