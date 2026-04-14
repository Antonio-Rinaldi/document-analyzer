"""Detailed module documentation for `src/document_analyzer_api/domain/ports/document_parser.py`.

File role:
- Located in the domain port layer.
- Defines logic and symbols for `document_parser.py` within Document Analyzer V1.

Purpose:
- Declares abstract contracts implemented by infrastructure adapters.

Exported symbols overview:
- Classes: DocumentParserPort.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from typing import Protocol

from ..models.chunking import ParsedDocument


class DocumentParserPort(Protocol):
    """Detailed class documentation for `DocumentParserPort`.
    
    This component belongs to `src/document_analyzer_api/domain/ports/document_parser.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def supported_extensions(self) -> tuple[str, ...]:
        """Detailed synchronous function documentation for `supported_extensions`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/document_parser.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `supported_extensions` contract and consumed by downstream callers.
        """
        ...

    async def parse(self, document_name: str, content: bytes) -> ParsedDocument:
        """Detailed asynchronous function documentation for `parse`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/document_parser.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Parses incoming payloads into structured objects used by downstream flows.
        
            Args:
                document_name: Input parameter for `parse`.
                content: Raw payload bytes or text handled by the callable.
        
            Returns:
                Value defined by `parse` contract and consumed by downstream callers.
        """
        ...

