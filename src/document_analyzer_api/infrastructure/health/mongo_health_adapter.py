from document_analyzer_api.domain.ports.health import DependencyStatus


class MongoHealthAdapter:
    def __init__(self, uri: str, timeout_seconds: float) -> None:
        self._uri = uri
        self._timeout_ms = int(timeout_seconds * 1000)

    async def check(self) -> DependencyStatus:
        try:
            from pymongo import MongoClient

            with MongoClient(self._uri, serverSelectionTimeoutMS=self._timeout_ms) as client:
                client.admin.command("ping")
            return DependencyStatus(name="mongodb", ok=True, detail="reachable")
        except Exception as exc:
            return DependencyStatus(name="mongodb", ok=False, detail=str(exc))


