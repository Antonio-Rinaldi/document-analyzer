"""Module `src/document_analyzer_api/domain/ports/health.py`.

This module belongs to the domain abstraction layer of Document Analyzer.

Purpose:
- Declares protocol contracts implemented by infrastructure adapters.

Defined symbols:
- Classes: DependencyStatus, DependencyHealthPort.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class DependencyStatus:
    """DependencyStatus component.
    
    This class is defined in `src/document_analyzer_api/domain/ports/health.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: name, ok, detail.
    """
    name: str
    ok: bool
    detail: str


class DependencyHealthPort(Protocol):
    """DependencyHealthPort component.
    
    This class is defined in `src/document_analyzer_api/domain/ports/health.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """

    async def check(self) -> DependencyStatus:
        """Asynchronous execution path for `check`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/health.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                None.
        
            Returns:
                A value compatible with `DependencyStatus`.
        """
        ...

