"""Detailed module documentation for `src/document_analyzer_api/infrastructure/parsing/markitdown_document_parser.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `markitdown_document_parser.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: MarkItDownDocumentParser.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
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
    """Detailed class documentation for `MarkItDownDocumentParser`.
    
    This component belongs to `src/document_analyzer_api/infrastructure/parsing/markitdown_document_parser.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/parsing/markitdown_document_parser.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._markitdown = MarkItDown(enable_plugins=False)
        self._supported_extensions = discover_supported_input_extensions()

    def supported_extensions(self) -> tuple[str, ...]:
        """Detailed synchronous function documentation for `supported_extensions`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/parsing/markitdown_document_parser.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `supported_extensions` contract and consumed by downstream callers.
        """
        return self._supported_extensions

    async def parse(self, document_name: str, content: bytes) -> ParsedDocument:
        """Detailed asynchronous function documentation for `parse`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/parsing/markitdown_document_parser.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Parses incoming payloads into structured objects used by downstream flows.
        
            Args:
                document_name: Input parameter for `parse`.
                content: Raw payload bytes or text handled by the callable.
        
            Returns:
                Value defined by `parse` contract and consumed by downstream callers.
        """
        extension = Path(document_name).suffix.lower()
        result = self._markitdown.convert_stream(BytesIO(content), file_extension=extension or None)
        text = (result.text_content or "").strip()
        if not text:
            text = "Empty document"

        sections = self._to_sections(document_name=document_name, text=text)
        return ParsedDocument(document_name=document_name, sections=sections)

    def _to_sections(self, *, document_name: str, text: str) -> list[ParsedSection]:
        """Detailed synchronous function documentation for `_to_sections`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/parsing/markitdown_document_parser.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                document_name: Input parameter for `_to_sections`.
                text: Input parameter for `_to_sections`.
        
            Returns:
                Value defined by `_to_sections` contract and consumed by downstream callers.
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

