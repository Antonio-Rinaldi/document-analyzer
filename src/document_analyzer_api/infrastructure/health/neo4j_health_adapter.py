from document_analyzer_api.domain.ports.health import DependencyStatus


class Neo4jHealthAdapter:
    def __init__(self, uri: str, user: str, password: str, timeout_seconds: float) -> None:
        self._uri = uri
        self._user = user
        self._password = password
        self._timeout_seconds = timeout_seconds

    async def check(self) -> DependencyStatus:
        try:
            from neo4j import GraphDatabase

            driver = GraphDatabase.driver(self._uri, auth=(self._user, self._password))
            with driver.session() as session:
                session.run("RETURN 1").single()
            driver.close()
            return DependencyStatus(name="neo4j", ok=True, detail="reachable")
        except Exception as exc:
            return DependencyStatus(name="neo4j", ok=False, detail=str(exc))


