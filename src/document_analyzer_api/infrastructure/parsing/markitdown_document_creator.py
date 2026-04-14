"""Detailed module documentation for `src/document_analyzer_api/infrastructure/parsing/markitdown_document_creator.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `markitdown_document_creator.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: MarkItDownDocumentCreator.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from __future__ import annotations

from ...domain.ports.document_creator import CreatedDocument, DocumentCreatorPort
from ..markitdown.capabilities import SUPPORTED_OUTPUT_FORMATS


class MarkItDownDocumentCreator(DocumentCreatorPort):
    """Detailed class documentation for `MarkItDownDocumentCreator`.
    
    This component belongs to `src/document_analyzer_api/infrastructure/parsing/markitdown_document_creator.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def supported_output_formats(self) -> tuple[str, ...]:
        """Detailed synchronous function documentation for `supported_output_formats`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/parsing/markitdown_document_creator.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `supported_output_formats` contract and consumed by downstream callers.
        """
        return SUPPORTED_OUTPUT_FORMATS

    async def create(self, *, summary_text: str, output_format: str, filename_stem: str) -> CreatedDocument:
        """Detailed asynchronous function documentation for `create`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/parsing/markitdown_document_creator.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                summary_text: Input parameter for `create`.
                output_format: Input parameter for `create`.
                filename_stem: Input parameter for `create`.
        
            Returns:
                Value defined by `create` contract and consumed by downstream callers.
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
        """Detailed synchronous function documentation for `_to_plain_text`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/parsing/markitdown_document_creator.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                markdown_text: Input parameter for `_to_plain_text`.
        
            Returns:
                Value defined by `_to_plain_text` contract and consumed by downstream callers.
        """
        return "\n".join(line.lstrip("#").strip() for line in markdown_text.splitlines()).strip()
