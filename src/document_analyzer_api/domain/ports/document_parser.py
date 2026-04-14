"""Module `src/document_analyzer_api/domain/ports/document_parser.py`.

This module belongs to the domain abstraction layer of Document Analyzer.

Purpose:
- Declares protocol contracts implemented by infrastructure adapters.

Defined symbols:
- Classes: DocumentParserPort.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from typing import Protocol

from ..models.chunking import ParsedDocument


class DocumentParserPort(Protocol):
    """DocumentParserPort component.
    
    This class is defined in `src/document_analyzer_api/domain/ports/document_parser.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def supported_extensions(self) -> tuple[str, ...]:
        """Synchronous execution path for `supported_extensions`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/document_parser.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                None.
        
            Returns:
                A value compatible with `tuple[str, ...]`.
        """
        ...

    async def parse(self, document_name: str, content: bytes) -> ParsedDocument:
        """Asynchronous execution path for `parse`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/document_parser.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Parses incoming payloads and converts them to structured internal objects.
        
            Args:
                document_name: Input parameter accepted by `parse`.
                content: Raw payload bytes/text processed or transformed by this callable.
        
            Returns:
                A value compatible with `ParsedDocument`.
        """
        ...

