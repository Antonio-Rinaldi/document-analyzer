"""Module `src/document_analyzer_api/infrastructure/storage/local_output_storage.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: LocalOutputStorage.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import asyncio
from pathlib import Path


class LocalOutputStorage:
    """LocalOutputStorage component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/storage/local_output_storage.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, root_path: str) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_output_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (Path) to satisfy the callable contract.
        
            Args:
                root_path: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._root = Path(root_path) / "output"

    async def write_output(self, filename: str, content: bytes, content_type: str | None = None) -> str:
        """Asynchronous execution path for `write_output`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_output_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (mkdir, to_thread, write_bytes) to satisfy the callable contract.
        
            Args:
                filename: Input parameter accepted by `write_output`.
                content: Raw payload bytes/text processed or transformed by this callable.
                content_type: Input parameter accepted by `write_output`.
        
            Returns:
                A value compatible with `str`.
        """
        path = self._root / filename

        def _write() -> None:
            """Synchronous execution path for `_write`.
            
            This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_output_storage.py` and contributes to module-level behavior
            with explicit and testable execution semantics.
            
                Behavior:
                    Coordinates helper calls (mkdir, write_bytes) to satisfy the callable contract.
            
                Args:
                    None.
            
                Returns:
                    A value compatible with `None`.
            """
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)

        await asyncio.to_thread(_write)
        return f"local://output/{filename}"

