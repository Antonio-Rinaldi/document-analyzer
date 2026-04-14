"""Module `src/document_analyzer_api/infrastructure/parsing/simple_epub_parser.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: SimpleEpubParser.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import re
import zipfile
from io import BytesIO
from pathlib import Path

from ...domain.models.chunking import ParsedDocument, ParsedSection
from ...domain.ports.document_parser import DocumentParserPort


class SimpleEpubParser(DocumentParserPort):
    """SimpleEpubParser component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/parsing/simple_epub_parser.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    async def parse(self, document_name: str, content: bytes) -> ParsedDocument:
        """Asynchronous execution path for `parse`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/parsing/simple_epub_parser.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Parses incoming payloads and converts them to structured internal objects.
        
            Args:
                document_name: Input parameter accepted by `parse`.
                content: Raw payload bytes/text processed or transformed by this callable.
        
            Returns:
                A value compatible with `ParsedDocument`.
        """
        sections = self._parse_from_zip(content)
        if not sections:
            fallback_text = content.decode("utf-8", errors="ignore").strip()
            if not fallback_text:
                fallback_text = "Empty document"
            sections = [ParsedSection(section_id="section-0", title=Path(document_name).name, text=fallback_text)]

        return ParsedDocument(document_name=document_name, sections=sections)

    def _parse_from_zip(self, content: bytes) -> list[ParsedSection]:
        """Synchronous execution path for `_parse_from_zip`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/parsing/simple_epub_parser.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (BytesIO, ParsedSection, Path, ZipFile) to satisfy the callable contract.
        
            Args:
                content: Raw payload bytes/text processed or transformed by this callable.
        
            Returns:
                A value compatible with `list[ParsedSection]`.
        """
        sections: list[ParsedSection] = []
        try:
            with zipfile.ZipFile(BytesIO(content)) as archive:
                html_files = [
                    name
                    for name in archive.namelist()
                    if name.lower().endswith((".xhtml", ".html", ".htm"))
                ]
                html_files.sort()
                for index, name in enumerate(html_files):
                    raw = archive.read(name).decode("utf-8", errors="ignore")
                    text = self._extract_text(raw)
                    if text:
                        sections.append(
                            ParsedSection(
                                section_id=f"section-{index}",
                                title=Path(name).name,
                                text=text,
                            )
                        )
        except zipfile.BadZipFile:
            return []

        return sections

    def _extract_text(self, html: str) -> str:
        """Synchronous execution path for `_extract_text`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/parsing/simple_epub_parser.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (join, split, sub) to satisfy the callable contract.
        
            Args:
                html: Input parameter accepted by `_extract_text`.
        
            Returns:
                A value compatible with `str`.
        """
        no_scripts = re.sub(r"<script.*?>.*?</script>", " ", html, flags=re.IGNORECASE | re.DOTALL)
        no_styles = re.sub(r"<style.*?>.*?</style>", " ", no_scripts, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", no_styles)
        normalized = " ".join(text.split())
        return normalized

