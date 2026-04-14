"""Detailed module documentation for `src/document_analyzer_api/domain/ports/health.py`.

File role:
- Located in the domain port layer.
- Defines logic and symbols for `health.py` within Document Analyzer V1.

Purpose:
- Declares abstract contracts implemented by infrastructure adapters.

Exported symbols overview:
- Classes: DependencyStatus, DependencyHealthPort.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class DependencyStatus:
    """Detailed class documentation for `DependencyStatus`.
    
    This component belongs to `src/document_analyzer_api/domain/ports/health.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    name: str
    ok: bool
    detail: str


class DependencyHealthPort(Protocol):
    """Detailed class documentation for `DependencyHealthPort`.
    
    This component belongs to `src/document_analyzer_api/domain/ports/health.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """

    async def check(self) -> DependencyStatus:
        """Detailed asynchronous function documentation for `check`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/health.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `check` contract and consumed by downstream callers.
        """
        ...

