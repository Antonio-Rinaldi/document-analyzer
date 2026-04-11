import re
import zipfile
from io import BytesIO
from pathlib import Path

from ...domain.models.chunking import ParsedDocument, ParsedSection
from ...domain.ports.document_parser import DocumentParserPort


class SimpleEpubParser(DocumentParserPort):
    async def parse(self, document_name: str, content: bytes) -> ParsedDocument:
        sections = self._parse_from_zip(content)
        if not sections:
            fallback_text = content.decode("utf-8", errors="ignore").strip()
            if not fallback_text:
                fallback_text = "Empty document"
            sections = [ParsedSection(section_id="section-0", title=Path(document_name).name, text=fallback_text)]

        return ParsedDocument(document_name=document_name, sections=sections)

    def _parse_from_zip(self, content: bytes) -> list[ParsedSection]:
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
        no_scripts = re.sub(r"<script.*?>.*?</script>", " ", html, flags=re.IGNORECASE | re.DOTALL)
        no_styles = re.sub(r"<style.*?>.*?</style>", " ", no_scripts, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", no_styles)
        normalized = " ".join(text.split())
        return normalized

