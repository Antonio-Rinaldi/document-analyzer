"""Module `src/document_analyzer_api/infrastructure/parsing/markitdown_document_creator.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: MarkItDownDocumentCreator.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from __future__ import annotations

from ...domain.ports.document_creator import CreatedDocument, DocumentCreatorPort
from ..markitdown.capabilities import SUPPORTED_OUTPUT_FORMATS


class MarkItDownDocumentCreator(DocumentCreatorPort):
    """MarkItDownDocumentCreator component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/parsing/markitdown_document_creator.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def supported_output_formats(self) -> tuple[str, ...]:
        """Synchronous execution path for `supported_output_formats`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/parsing/markitdown_document_creator.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                None.
        
            Returns:
                A value compatible with `tuple[str, ...]`.
        """
        return SUPPORTED_OUTPUT_FORMATS

    async def create(self, *, summary_text: str, output_format: str, filename_stem: str) -> CreatedDocument:
        """Asynchronous execution path for `create`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/parsing/markitdown_document_creator.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (CreatedDocument, ValueError, _to_plain_text, encode) to satisfy the callable contract.
        
            Args:
                summary_text: Input parameter accepted by `create`.
                output_format: Input parameter accepted by `create`.
                filename_stem: Input parameter accepted by `create`.
        
            Returns:
                A value compatible with `CreatedDocument`.
        """
        normalized = output_format.strip().lower()
        if normalized not in self.supported_output_formats():
            allowed = ", ".join(self.supported_output_formats())
            raise ValueError(f"Unsupported summary outputFormat '{output_format}'. Supported values: {allowed}")

        if normalized in {"md", "markdown"}:
            return CreatedDocument(filename=f"{filename_stem}.md", content=summary_text.encode("utf-8"))

        plain = self._to_plain_text(summary_text)
        return CreatedDocument(filename=f"{filename_stem}.txt", content=plain.encode("utf-8"))

    def _to_plain_text(self, markdown_text: str) -> str:
        """Synchronous execution path for `_to_plain_text`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/parsing/markitdown_document_creator.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (join, lstrip, splitlines, strip) to satisfy the callable contract.
        
            Args:
                markdown_text: Input parameter accepted by `_to_plain_text`.
        
            Returns:
                A value compatible with `str`.
        """
        return "\n".join(line.lstrip("#").strip() for line in markdown_text.splitlines()).strip()
