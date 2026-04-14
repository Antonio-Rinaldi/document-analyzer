"""Detailed module documentation for `src/document_analyzer_api/infrastructure/health/neo4j_health_adapter.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `neo4j_health_adapter.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: Neo4jHealthAdapter.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from document_analyzer_api.domain.ports.health import DependencyStatus


class Neo4jHealthAdapter:
    """Detailed class documentation for `Neo4jHealthAdapter`.
    
    This component belongs to `src/document_analyzer_api/infrastructure/health/neo4j_health_adapter.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, uri: str, user: str, password: str, timeout_seconds: float) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/health/neo4j_health_adapter.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                uri: Input parameter for `__init__`.
                user: Input parameter for `__init__`.
                password: Input parameter for `__init__`.
                timeout_seconds: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._uri = uri
        self._user = user
        self._password = password
        self._timeout_seconds = timeout_seconds

    async def check(self) -> DependencyStatus:
        """Detailed asynchronous function documentation for `check`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/health/neo4j_health_adapter.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `check` contract and consumed by downstream callers.
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


