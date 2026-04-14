"""Detailed module documentation for `src/document_analyzer_api/infrastructure/storage/s3_output_storage.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `s3_output_storage.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: S3OutputStorage.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

import asyncio
from io import BytesIO


class S3OutputStorage:
    """Detailed class documentation for `S3OutputStorage`.
    
    This component belongs to `src/document_analyzer_api/infrastructure/storage/s3_output_storage.py` and encapsulates one cohesive responsibility in the
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
    ) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_output_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                endpoint: Input parameter for `__init__`.
                access_key: Input parameter for `__init__`.
                secret_key: Input parameter for `__init__`.
                bucket: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        from minio import Minio

        self._bucket = bucket
        self._client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=False)

    async def write_output(self, filename: str, content: bytes, content_type: str | None = None) -> str:
        """Detailed asynchronous function documentation for `write_output`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_output_storage.py` and contributes to the module workflow
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
        await asyncio.to_thread(self._write_sync, filename, content, content_type)
        return f"s3://{self._bucket}/{filename}"

    def _ensure_bucket(self) -> None:
        """Detailed synchronous function documentation for `_ensure_bucket`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_output_storage.py` and contributes to the module workflow
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

    def _write_sync(self, filename: str, content: bytes, content_type: str | None) -> None:
        """Detailed synchronous function documentation for `_write_sync`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/storage/s3_output_storage.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                filename: Input parameter for `_write_sync`.
                content: Raw payload bytes or text handled by the callable.
                content_type: Input parameter for `_write_sync`.
        
            Returns:
                Value defined by `_write_sync` contract and consumed by downstream callers.
        """
        self._ensure_bucket()
        self._client.put_object(
            self._bucket,
            filename,
            BytesIO(content),
            length=len(content),
            content_type=content_type,
        )

