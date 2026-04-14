"""Detailed module documentation for `src/document_analyzer_api/infrastructure/storage/local_document_storage.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `local_document_storage.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: LocalDocumentStorage.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

import asyncio
import hashlib
from pathlib import Path


class LocalDocumentStorage:
    """Detailed class documentation for `LocalDocumentStorage`.
    
    This component belongs to `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, root_path: str, done_extension: str = ".done") -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                root_path: Input parameter for `__init__`.
                done_extension: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._root_path = Path(root_path)
        self._done_extension = done_extension

    async def object_exists(self, name: str) -> bool:
        """Detailed asynchronous function documentation for `object_exists`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                name: Environment variable or entity name, depending on callable context.
        
            Returns:
                Value defined by `object_exists` contract and consumed by downstream callers.
        """
        path = self._object_path(name)
        return await asyncio.to_thread(path.exists)

    async def object_hash(self, name: str) -> str:
        """Detailed asynchronous function documentation for `object_hash`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                name: Environment variable or entity name, depending on callable context.
        
            Returns:
                Value defined by `object_hash` contract and consumed by downstream callers.
        """
        path = self._object_path(name)

        def _read_hash() -> str:
            """Detailed synchronous function documentation for `_read_hash`.
            
            This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and contributes to the module workflow
            through deterministic input/output behavior and explicit collaboration contracts.
            
                Behavior:
                    Executes the callable contract for this module responsibility.
            
                Args:
                    None.
            
                Returns:
                    Value defined by `_read_hash` contract and consumed by downstream callers.
            """
            hasher = hashlib.sha256()
            with path.open("rb") as handle:
                while chunk := handle.read(1024 * 1024):
                    hasher.update(chunk)
            return hasher.hexdigest()

        return await asyncio.to_thread(_read_hash)

    async def put_object(self, name: str, content: bytes) -> None:
        """Detailed asynchronous function documentation for `put_object`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                name: Environment variable or entity name, depending on callable context.
                content: Raw payload bytes or text handled by the callable.
        
            Returns:
                Value defined by `put_object` contract and consumed by downstream callers.
        """
        path = self._object_path(name)

        def _write() -> None:
            """Detailed synchronous function documentation for `_write`.
            
            This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and contributes to the module workflow
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

    async def has_done_marker(self, name: str) -> bool:
        """Detailed asynchronous function documentation for `has_done_marker`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                name: Environment variable or entity name, depending on callable context.
        
            Returns:
                Value defined by `has_done_marker` contract and consumed by downstream callers.
        """
        marker = self._done_path(name)
        return await asyncio.to_thread(marker.exists)

    async def write_done_marker(self, name: str) -> None:
        """Detailed asynchronous function documentation for `write_done_marker`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                name: Environment variable or entity name, depending on callable context.
        
            Returns:
                Value defined by `write_done_marker` contract and consumed by downstream callers.
        """
        marker = self._done_path(name)

        def _write() -> None:
            """Detailed synchronous function documentation for `_write`.
            
            This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and contributes to the module workflow
            through deterministic input/output behavior and explicit collaboration contracts.
            
                Behavior:
                    Executes the callable contract for this module responsibility.
            
                Args:
                    None.
            
                Returns:
                    Value defined by `_write` contract and consumed by downstream callers.
            """
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_text("", encoding="utf-8")

        await asyncio.to_thread(_write)

    def _object_path(self, name: str) -> Path:
        """Detailed synchronous function documentation for `_object_path`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                name: Environment variable or entity name, depending on callable context.
        
            Returns:
                Value defined by `_object_path` contract and consumed by downstream callers.
        """
        safe_name = Path(name).name
        if safe_name != name:
            raise ValueError("File name must not include directory segments")
        return self._root_path / safe_name

    def _done_path(self, name: str) -> Path:
        """Detailed synchronous function documentation for `_done_path`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/local_document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                name: Environment variable or entity name, depending on callable context.
        
            Returns:
                Value defined by `_done_path` contract and consumed by downstream callers.
        """
        return self._root_path / f"{Path(name).name}{self._done_extension}"

