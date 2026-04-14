"""Detailed module documentation for `src/document_analyzer_api/infrastructure/parsing/simple_epub_parser.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `simple_epub_parser.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: SimpleEpubParser.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

import re
import zipfile
from io import BytesIO
from pathlib import Path

from ...domain.models.chunking import ParsedDocument, ParsedSection
from ...domain.ports.document_parser import DocumentParserPort


class SimpleEpubParser(DocumentParserPort):
    """Detailed class documentation for `SimpleEpubParser`.
    
    This component belongs to `src/document_analyzer_api/infrastructure/parsing/simple_epub_parser.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    async def parse(self, document_name: str, content: bytes) -> ParsedDocument:
        """Detailed asynchronous function documentation for `parse`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/parsing/simple_epub_parser.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Parses incoming payloads into structured objects used by downstream flows.
        
            Args:
                document_name: Input parameter for `parse`.
                content: Raw payload bytes or text handled by the callable.
        
            Returns:
                Value defined by `parse` contract and consumed by downstream callers.
        """
        sections = self._parse_from_zip(content)
        if not sections:
            fallback_text = content.decode("utf-8", errors="ignore").strip()
            if not fallback_text:
                fallback_text = "Empty document"
            sections = [ParsedSection(section_id="section-0", title=Path(document_name).name, text=fallback_text)]

        return ParsedDocument(document_name=document_name, sections=sections)

    def _parse_from_zip(self, content: bytes) -> list[ParsedSection]:
        """Detailed synchronous function documentation for `_parse_from_zip`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/parsing/simple_epub_parser.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                content: Raw payload bytes or text handled by the callable.
        
            Returns:
                Value defined by `_parse_from_zip` contract and consumed by downstream callers.
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
        """Detailed synchronous function documentation for `_extract_text`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/parsing/simple_epub_parser.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                html: Input parameter for `_extract_text`.
        
            Returns:
                Value defined by `_extract_text` contract and consumed by downstream callers.
        """
        no_scripts = re.sub(r"<script.*?>.*?</script>", " ", html, flags=re.IGNORECASE | re.DOTALL)
        no_styles = re.sub(r"<style.*?>.*?</style>", " ", no_scripts, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", no_styles)
        normalized = " ".join(text.split())
        return normalized

