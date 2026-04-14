"""Module `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: S3DocumentStorage.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import asyncio
import hashlib
from io import BytesIO


class S3DocumentStorage:
    """S3DocumentStorage component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(
        self,
        *,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        done_extension: str,
    ) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (Minio) to satisfy the callable contract.
        
            Args:
                endpoint: Input parameter accepted by `__init__`.
                access_key: Input parameter accepted by `__init__`.
                secret_key: Input parameter accepted by `__init__`.
                bucket: Input parameter accepted by `__init__`.
                done_extension: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        from minio import Minio

        self._bucket = bucket
        self._done_extension = done_extension
        self._client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=False)

    async def object_exists(self, name: str) -> bool:
        """Asynchronous execution path for `object_exists`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (to_thread) to satisfy the callable contract.
        
            Args:
                name: Identifier/environment key consumed by this callable.
        
            Returns:
                A value compatible with `bool`.
        """
        return await asyncio.to_thread(self._object_exists_sync, name)

    async def object_hash(self, name: str) -> str:
        """Asynchronous execution path for `object_hash`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (to_thread) to satisfy the callable contract.
        
            Args:
                name: Identifier/environment key consumed by this callable.
        
            Returns:
                A value compatible with `str`.
        """
        return await asyncio.to_thread(self._object_hash_sync, name)

    async def put_object(self, name: str, content: bytes) -> None:
        """Asynchronous execution path for `put_object`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (to_thread) to satisfy the callable contract.
        
            Args:
                name: Identifier/environment key consumed by this callable.
                content: Raw payload bytes/text processed or transformed by this callable.
        
            Returns:
                A value compatible with `None`.
        """
        await asyncio.to_thread(self._put_object_sync, name, content)

    async def has_done_marker(self, name: str) -> bool:
        """Asynchronous execution path for `has_done_marker`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (to_thread) to satisfy the callable contract.
        
            Args:
                name: Identifier/environment key consumed by this callable.
        
            Returns:
                A value compatible with `bool`.
        """
        marker = f"{name}{self._done_extension}"
        return await asyncio.to_thread(self._object_exists_sync, marker)

    async def write_done_marker(self, name: str) -> None:
        """Asynchronous execution path for `write_done_marker`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (to_thread) to satisfy the callable contract.
        
            Args:
                name: Identifier/environment key consumed by this callable.
        
            Returns:
                A value compatible with `None`.
        """
        marker = f"{name}{self._done_extension}"
        await asyncio.to_thread(self._put_object_sync, marker, b"")

    def _ensure_bucket(self) -> None:
        """Synchronous execution path for `_ensure_bucket`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (bucket_exists, make_bucket) to satisfy the callable contract.
        
            Args:
                None.
        
            Returns:
                A value compatible with `None`.
        """
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)

    def _object_exists_sync(self, name: str) -> bool:
        """Synchronous execution path for `_object_exists_sync`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (_ensure_bucket, stat_object) to satisfy the callable contract.
        
            Args:
                name: Identifier/environment key consumed by this callable.
        
            Returns:
                A value compatible with `bool`.
        """
        self._ensure_bucket()
        try:
            self._client.stat_object(self._bucket, name)
            return True
        except Exception:
            return False

    def _object_hash_sync(self, name: str) -> str:
        """Synchronous execution path for `_object_hash_sync`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (_ensure_bucket, close, get_object, hexdigest) to satisfy the callable contract.
        
            Args:
                name: Identifier/environment key consumed by this callable.
        
            Returns:
                A value compatible with `str`.
        """
        self._ensure_bucket()
        response = self._client.get_object(self._bucket, name)
        try:
            hasher = hashlib.sha256()
            for chunk in response.stream(1024 * 1024):
                hasher.update(chunk)
            return hasher.hexdigest()
        finally:
            response.close()
            response.release_conn()

    def _put_object_sync(self, name: str, content: bytes) -> None:
        """Synchronous execution path for `_put_object_sync`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (BytesIO, _ensure_bucket, len, put_object) to satisfy the callable contract.
        
            Args:
                name: Identifier/environment key consumed by this callable.
                content: Raw payload bytes/text processed or transformed by this callable.
        
            Returns:
                A value compatible with `None`.
        """
        self._ensure_bucket()
        data = BytesIO(content)
        self._client.put_object(self._bucket, name, data, length=len(content))

