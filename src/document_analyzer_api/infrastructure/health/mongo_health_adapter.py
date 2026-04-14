"""Module `src/document_analyzer_api/infrastructure/health/mongo_health_adapter.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: MongoHealthAdapter.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from document_analyzer_api.domain.ports.health import DependencyStatus


class MongoHealthAdapter:
    """MongoHealthAdapter component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/health/mongo_health_adapter.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, uri: str, timeout_seconds: float) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/health/mongo_health_adapter.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (int) to satisfy the callable contract.
        
            Args:
                uri: Input parameter accepted by `__init__`.
                timeout_seconds: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._uri = uri
        self._timeout_ms = int(timeout_seconds * 1000)

    async def check(self) -> DependencyStatus:
        """Asynchronous execution path for `check`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/health/mongo_health_adapter.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (DependencyStatus, MongoClient, command, str) to satisfy the callable contract.
        
            Args:
                None.
        
            Returns:
                A value compatible with `DependencyStatus`.
        """
        try:
            from pymongo import MongoClient

            with MongoClient(self._uri, serverSelectionTimeoutMS=self._timeout_ms) as client:
                client.admin.command("ping")
            return DependencyStatus(name="mongodb", ok=True, detail="reachable")
        except Exception as exc:
            return DependencyStatus(name="mongodb", ok=False, detail=str(exc))


