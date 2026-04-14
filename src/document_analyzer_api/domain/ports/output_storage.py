"""Module `src/document_analyzer_api/domain/ports/output_storage.py`.

This module belongs to the domain abstraction layer of Document Analyzer.

Purpose:
- Declares protocol contracts implemented by infrastructure adapters.

Defined symbols:
- Classes: OutputStoragePort.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from typing import Protocol


class OutputStoragePort(Protocol):
    """OutputStoragePort component.
    
    This class is defined in `src/document_analyzer_api/domain/ports/output_storage.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    async def write_output(self, filename: str, content: bytes, content_type: str | None = None) -> str:
        """Asynchronous execution path for `write_output`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/output_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                filename: Input parameter accepted by `write_output`.
                content: Raw payload bytes/text processed or transformed by this callable.
                content_type: Input parameter accepted by `write_output`.
        
            Returns:
                A value compatible with `str`.
        """
        ...

