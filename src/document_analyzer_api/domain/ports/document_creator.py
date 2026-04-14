"""Module `src/document_analyzer_api/domain/ports/document_creator.py`.

This module belongs to the domain abstraction layer of Document Analyzer.

Purpose:
- Declares protocol contracts implemented by infrastructure adapters.

Defined symbols:
- Classes: CreatedDocument, DocumentCreatorPort.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class CreatedDocument:
    """CreatedDocument component.
    
    This class is defined in `src/document_analyzer_api/domain/ports/document_creator.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: filename, content.
    """
    filename: str
    content: bytes


class DocumentCreatorPort(Protocol):
    """DocumentCreatorPort component.
    
    This class is defined in `src/document_analyzer_api/domain/ports/document_creator.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def supported_output_formats(self) -> tuple[str, ...]:
        """Synchronous execution path for `supported_output_formats`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/document_creator.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                None.
        
            Returns:
                A value compatible with `tuple[str, ...]`.
        """
        ...

    async def create(self, *, summary_text: str, output_format: str, filename_stem: str) -> CreatedDocument:
        """Asynchronous execution path for `create`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/document_creator.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                summary_text: Input parameter accepted by `create`.
                output_format: Input parameter accepted by `create`.
                filename_stem: Input parameter accepted by `create`.
        
            Returns:
                A value compatible with `CreatedDocument`.
        """
        ...

