"""Detailed module documentation for `src/document_analyzer_api/infrastructure/health/minio_health_adapter.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `minio_health_adapter.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: MinioHealthAdapter.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from document_analyzer_api.domain.ports.health import DependencyStatus


class MinioHealthAdapter:
    """Detailed class documentation for `MinioHealthAdapter`.
    
    This component belongs to `src/document_analyzer_api/infrastructure/health/minio_health_adapter.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, endpoint: str, access_key: str, secret_key: str, timeout_seconds: float) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/health/minio_health_adapter.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                endpoint: Input parameter for `__init__`.
                access_key: Input parameter for `__init__`.
                secret_key: Input parameter for `__init__`.
                timeout_seconds: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._endpoint = endpoint
        self._access_key = access_key
        self._secret_key = secret_key
        self._timeout_seconds = timeout_seconds

    async def check(self) -> DependencyStatus:
        """Detailed asynchronous function documentation for `check`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/health/minio_health_adapter.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `check` contract and consumed by downstream callers.
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


