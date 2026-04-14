"""Detailed module documentation for `src/document_analyzer_api/infrastructure/storage/local_output_storage.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `local_output_storage.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: LocalOutputStorage.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

import asyncio
from pathlib import Path


class LocalOutputStorage:
    """Detailed class documentation for `LocalOutputStorage`.
    
    This component belongs to `src/document_analyzer_api/infrastructure/storage/local_output_storage.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, root_path: str) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_output_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                root_path: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._root = Path(root_path) / "output"

    async def write_output(self, filename: str, content: bytes, content_type: str | None = None) -> str:
        """Detailed asynchronous function documentation for `write_output`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_output_storage.py` and contributes to the module workflow
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
        path = self._root / filename

        def _write() -> None:
            """Detailed synchronous function documentation for `_write`.
            
            This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_output_storage.py` and contributes to the module workflow
            through deterministic input/output behavior and explicit collaboration contracts.
            
                Behavior:
                    Executes the callable contract for this module responsibility.
            
                Args:
                    None.
            
                Returns:
                    Value defined by `_write` contract and consumed by downstream callers.
            """
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)

        await asyncio.to_thread(_write)
        return f"local://output/{filename}"

