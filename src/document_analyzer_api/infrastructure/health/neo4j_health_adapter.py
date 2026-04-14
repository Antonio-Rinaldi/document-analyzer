"""Module `src/document_analyzer_api/infrastructure/health/neo4j_health_adapter.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: Neo4jHealthAdapter.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from document_analyzer_api.domain.ports.health import DependencyStatus


class Neo4jHealthAdapter:
    """Neo4jHealthAdapter component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/health/neo4j_health_adapter.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, uri: str, user: str, password: str, timeout_seconds: float) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/health/neo4j_health_adapter.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                uri: Input parameter accepted by `__init__`.
                user: Input parameter accepted by `__init__`.
                password: Input parameter accepted by `__init__`.
                timeout_seconds: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._uri = uri
        self._user = user
        self._password = password
        self._timeout_seconds = timeout_seconds

    async def check(self) -> DependencyStatus:
        """Asynchronous execution path for `check`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/health/neo4j_health_adapter.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (DependencyStatus, close, driver, run) to satisfy the callable contract.
        
            Args:
                None.
        
            Returns:
                A value compatible with `DependencyStatus`.
        """
        try:
            from neo4j import GraphDatabase

            driver = GraphDatabase.driver(self._uri, auth=(self._user, self._password))
            with driver.session() as session:
                session.run("RETURN 1").single()
            driver.close()
            return DependencyStatus(name="neo4j", ok=True, detail="reachable")
        except Exception as exc:
            return DependencyStatus(name="neo4j", ok=False, detail=str(exc))


