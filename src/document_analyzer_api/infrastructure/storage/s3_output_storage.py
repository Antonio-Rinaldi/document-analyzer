"""Module `src/document_analyzer_api/infrastructure/storage/s3_output_storage.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: S3OutputStorage.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import asyncio
from datetime import timedelta
from io import BytesIO


class S3OutputStorage:
    """S3OutputStorage component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/storage/s3_output_storage.py` and encapsulates a single cohesive concern.
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
        presign_ttl_seconds: int,
    ) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_output_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (Minio) to satisfy the callable contract.
        
            Args:
                endpoint: Input parameter accepted by `__init__`.
                access_key: Input parameter accepted by `__init__`.
                secret_key: Input parameter accepted by `__init__`.
                bucket: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        from minio import Minio

        self._bucket = bucket
        self._presign_ttl = timedelta(seconds=presign_ttl_seconds)
        self._client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=False)

    async def write_output(self, filename: str, content: bytes, content_type: str | None = None) -> str:
        """Asynchronous execution path for `write_output`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_output_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (to_thread) to satisfy the callable contract.
        
            Args:
                filename: Input parameter accepted by `write_output`.
                content: Raw payload bytes/text processed or transformed by this callable.
                content_type: Input parameter accepted by `write_output`.
        
            Returns:
                A value compatible with `str`.
        """
        await asyncio.to_thread(self._write_sync, filename, content, content_type)
        return await asyncio.to_thread(self._presigned_download_url, filename)

    def _presigned_download_url(self, filename: str) -> str:
        """Build a presigned download URL for one stored output object."""
        return self._client.presigned_get_object(
            self._bucket,
            filename,
            expires=self._presign_ttl,
        )

    def _ensure_bucket(self) -> None:
        """Synchronous execution path for `_ensure_bucket`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_output_storage.py` and contributes to module-level behavior
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

    def _write_sync(self, filename: str, content: bytes, content_type: str | None) -> None:
        """Synchronous execution path for `_write_sync`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_output_storage.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (BytesIO, _ensure_bucket, len, put_object) to satisfy the callable contract.
        
            Args:
                filename: Input parameter accepted by `_write_sync`.
                content: Raw payload bytes/text processed or transformed by this callable.
                content_type: Input parameter accepted by `_write_sync`.
        
            Returns:
                A value compatible with `None`.
        """
        self._ensure_bucket()
        self._client.put_object(
            self._bucket,
            filename,
            BytesIO(content),
            length=len(content),
            content_type=content_type,
        )

