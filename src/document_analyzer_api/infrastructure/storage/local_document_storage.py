"""Module `src/document_analyzer_api/infrastructure/storage/local_document_storage.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: LocalDocumentStorage.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import asyncio
import hashlib
from pathlib import Path


class LocalDocumentStorage:
    """LocalDocumentStorage component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, root_path: str, done_extension: str = ".done") -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (Path) to satisfy the callable contract.
        
            Args:
                root_path: Input parameter accepted by `__init__`.
                done_extension: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._root_path = Path(root_path)
        self._done_extension = done_extension

    async def object_exists(self, name: str) -> bool:
        """Asynchronous execution path for `object_exists`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (_object_path, to_thread) to satisfy the callable contract.
        
            Args:
                name: Identifier/environment key consumed by this callable.
        
            Returns:
                A value compatible with `bool`.
        """
        path = self._object_path(name)
        return await asyncio.to_thread(path.exists)

    async def object_hash(self, name: str) -> str:
        """Asynchronous execution path for `object_hash`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (_object_path, hexdigest, open, read) to satisfy the callable contract.
        
            Args:
                name: Identifier/environment key consumed by this callable.
        
            Returns:
                A value compatible with `str`.
        """
        path = self._object_path(name)

        def _read_hash() -> str:
            """Synchronous execution path for `_read_hash`.
            
            This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and contributes to module-level behavior
            with explicit and testable execution semantics.
            
                Behavior:
                    Coordinates helper calls (hexdigest, open, read, sha256) to satisfy the callable contract.
            
                Args:
                    None.
            
                Returns:
                    A value compatible with `str`.
            """
            hasher = hashlib.sha256()
            with path.open("rb") as handle:
                while chunk := handle.read(1024 * 1024):
                    hasher.update(chunk)
            return hasher.hexdigest()

        return await asyncio.to_thread(_read_hash)

    async def put_object(self, name: str, content: bytes) -> None:
        """Asynchronous execution path for `put_object`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (_object_path, mkdir, to_thread, write_bytes) to satisfy the callable contract.
        
            Args:
                name: Identifier/environment key consumed by this callable.
                content: Raw payload bytes/text processed or transformed by this callable.
        
            Returns:
                A value compatible with `None`.
        """
        path = self._object_path(name)

        def _write() -> None:
            """Synchronous execution path for `_write`.
            
            This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and contributes to module-level behavior
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

    async def has_done_marker(self, name: str) -> bool:
        """Asynchronous execution path for `has_done_marker`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (_done_path, to_thread) to satisfy the callable contract.
        
            Args:
                name: Identifier/environment key consumed by this callable.
        
            Returns:
                A value compatible with `bool`.
        """
        marker = self._done_path(name)
        return await asyncio.to_thread(marker.exists)

    async def write_done_marker(self, name: str) -> None:
        """Asynchronous execution path for `write_done_marker`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (_done_path, mkdir, to_thread, write_text) to satisfy the callable contract.
        
            Args:
                name: Identifier/environment key consumed by this callable.
        
            Returns:
                A value compatible with `None`.
        """
        marker = self._done_path(name)

        def _write() -> None:
            """Synchronous execution path for `_write`.
            
            This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and contributes to module-level behavior
            with explicit and testable execution semantics.
            
                Behavior:
                    Coordinates helper calls (mkdir, write_text) to satisfy the callable contract.
            
                Args:
                    None.
            
                Returns:
                    A value compatible with `None`.
            """
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_text("", encoding="utf-8")

        await asyncio.to_thread(_write)

    def _object_path(self, name: str) -> Path:
        """Synchronous execution path for `_object_path`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (Path, ValueError) to satisfy the callable contract.
        
            Args:
                name: Identifier/environment key consumed by this callable.
        
            Returns:
                A value compatible with `Path`.
        """
        safe_name = Path(name).name
        if safe_name != name:
            raise ValueError("File name must not include directory segments")
        return self._root_path / safe_name

    def _done_path(self, name: str) -> Path:
        """Synchronous execution path for `_done_path`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (Path) to satisfy the callable contract.
        
            Args:
                name: Identifier/environment key consumed by this callable.
        
            Returns:
                A value compatible with `Path`.
        """
        return self._root_path / f"{Path(name).name}{self._done_extension}"

