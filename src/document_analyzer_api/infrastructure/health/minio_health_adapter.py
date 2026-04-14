"""Module `src/document_analyzer_api/infrastructure/health/minio_health_adapter.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: MinioHealthAdapter.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from document_analyzer_api.domain.ports.health import DependencyStatus


class MinioHealthAdapter:
    """MinioHealthAdapter component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/health/minio_health_adapter.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, endpoint: str, access_key: str, secret_key: str, timeout_seconds: float) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/health/minio_health_adapter.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                endpoint: Input parameter accepted by `__init__`.
                access_key: Input parameter accepted by `__init__`.
                secret_key: Input parameter accepted by `__init__`.
                timeout_seconds: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._endpoint = endpoint
        self._access_key = access_key
        self._secret_key = secret_key
        self._timeout_seconds = timeout_seconds

    async def check(self) -> DependencyStatus:
        """Asynchronous execution path for `check`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/health/minio_health_adapter.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (DependencyStatus, Minio, list_buckets, str) to satisfy the callable contract.
        
            Args:
                None.
        
            Returns:
                A value compatible with `DependencyStatus`.
        """
        try:
            from minio import Minio

            client = Minio(
                self._endpoint,
                access_key=self._access_key,
                secret_key=self._secret_key,
                secure=False,
            )
            # list_buckets triggers auth and connectivity checks.
            client.list_buckets()
            return DependencyStatus(name="minio", ok=True, detail="reachable")
        except Exception as exc:
            return DependencyStatus(name="minio", ok=False, detail=str(exc))


