"""Detailed module documentation for `src/document_analyzer_api/domain/ports/document_creator.py`.

File role:
- Located in the domain port layer.
- Defines logic and symbols for `document_creator.py` within Document Analyzer V1.

Purpose:
- Declares abstract contracts implemented by infrastructure adapters.

Exported symbols overview:
- Classes: CreatedDocument, DocumentCreatorPort.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class CreatedDocument:
    """Detailed class documentation for `CreatedDocument`.
    
    This component belongs to `src/document_analyzer_api/domain/ports/document_creator.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    filename: str
    content: bytes


class DocumentCreatorPort(Protocol):
    """Detailed class documentation for `DocumentCreatorPort`.
    
    This component belongs to `src/document_analyzer_api/domain/ports/document_creator.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def supported_output_formats(self) -> tuple[str, ...]:
        """Detailed synchronous function documentation for `supported_output_formats`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/document_creator.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `supported_output_formats` contract and consumed by downstream callers.
        """
        ...

    async def create(self, *, summary_text: str, output_format: str, filename_stem: str) -> CreatedDocument:
        """Detailed asynchronous function documentation for `create`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/document_creator.py` and contributes to the module workflow
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
        ...

