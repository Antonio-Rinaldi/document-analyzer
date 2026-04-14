"""Detailed module documentation for `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `s3_document_storage.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: S3DocumentStorage.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

import asyncio
import hashlib
from io import BytesIO


class S3DocumentStorage:
    """Detailed class documentation for `S3DocumentStorage`.
    
    This component belongs to `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
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
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                endpoint: Input parameter for `__init__`.
                access_key: Input parameter for `__init__`.
                secret_key: Input parameter for `__init__`.
                bucket: Input parameter for `__init__`.
                done_extension: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        from minio import Minio

        self._bucket = bucket
        self._done_extension = done_extension
        self._client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=False)

    async def object_exists(self, name: str) -> bool:
        """Detailed asynchronous function documentation for `object_exists`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                name: Environment variable or entity name, depending on callable context.
        
            Returns:
                Value defined by `object_exists` contract and consumed by downstream callers.
        """
        return await asyncio.to_thread(self._object_exists_sync, name)

    async def object_hash(self, name: str) -> str:
        """Detailed asynchronous function documentation for `object_hash`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                name: Environment variable or entity name, depending on callable context.
        
            Returns:
                Value defined by `object_hash` contract and consumed by downstream callers.
        """
        return await asyncio.to_thread(self._object_hash_sync, name)

    async def put_object(self, name: str, content: bytes) -> None:
        """Detailed asynchronous function documentation for `put_object`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                name: Environment variable or entity name, depending on callable context.
                content: Raw payload bytes or text handled by the callable.
        
            Returns:
                Value defined by `put_object` contract and consumed by downstream callers.
        """
        await asyncio.to_thread(self._put_object_sync, name, content)

    async def has_done_marker(self, name: str) -> bool:
        """Detailed asynchronous function documentation for `has_done_marker`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                name: Environment variable or entity name, depending on callable context.
        
            Returns:
                Value defined by `has_done_marker` contract and consumed by downstream callers.
        """
        marker = f"{name}{self._done_extension}"
        return await asyncio.to_thread(self._object_exists_sync, marker)

    async def write_done_marker(self, name: str) -> None:
        """Detailed asynchronous function documentation for `write_done_marker`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                name: Environment variable or entity name, depending on callable context.
        
            Returns:
                Value defined by `write_done_marker` contract and consumed by downstream callers.
        """
        marker = f"{name}{self._done_extension}"
        await asyncio.to_thread(self._put_object_sync, marker, b"")

    def _ensure_bucket(self) -> None:
        """Detailed synchronous function documentation for `_ensure_bucket`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `_ensure_bucket` contract and consumed by downstream callers.
        """
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)

    def _object_exists_sync(self, name: str) -> bool:
        """Detailed synchronous function documentation for `_object_exists_sync`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                name: Environment variable or entity name, depending on callable context.
        
            Returns:
                Value defined by `_object_exists_sync` contract and consumed by downstream callers.
        """
        self._ensure_bucket()
        try:
            self._client.stat_object(self._bucket, name)
            return True
        except Exception:
            return False

    def _object_hash_sync(self, name: str) -> str:
        """Detailed synchronous function documentation for `_object_hash_sync`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                name: Environment variable or entity name, depending on callable context.
        
            Returns:
                Value defined by `_object_hash_sync` contract and consumed by downstream callers.
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
        """Detailed synchronous function documentation for `_put_object_sync`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_document_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                name: Environment variable or entity name, depending on callable context.
                content: Raw payload bytes or text handled by the callable.
        
            Returns:
                Value defined by `_put_object_sync` contract and consumed by downstream callers.
        """
        self._ensure_bucket()
        data = BytesIO(content)
        self._client.put_object(self._bucket, name, data, length=len(content))

