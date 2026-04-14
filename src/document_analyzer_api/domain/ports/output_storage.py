"""Detailed module documentation for `src/document_analyzer_api/domain/ports/output_storage.py`.

File role:
- Located in the domain port layer.
- Defines logic and symbols for `output_storage.py` within Document Analyzer V1.

Purpose:
- Declares abstract contracts implemented by infrastructure adapters.

Exported symbols overview:
- Classes: OutputStoragePort.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from typing import Protocol


class OutputStoragePort(Protocol):
    """Detailed class documentation for `OutputStoragePort`.
    
    This component belongs to `src/document_analyzer_api/domain/ports/output_storage.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    async def write_output(self, filename: str, content: bytes, content_type: str | None = None) -> str:
        """Detailed asynchronous function documentation for `write_output`.
        
        This callable is implemented in `src/document_analyzer_api/domain/ports/output_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                filename: Input parameter for `write_output`.
                content: Raw payload bytes or text handled by the callable.
                content_type: Input parameter for `write_output`.
        
            Returns:
                Value defined by `write_output` contract and consumed by downstream callers.
        """
        ...

