from dataclasses import asdict, dataclass

from document_analyzer_api.domain.ports.health import DependencyHealthPort, DependencyStatus


@dataclass(slots=True)
class HealthReport:
    status: str
    dependencies: list[DependencyStatus]

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "dependencies": [asdict(item) for item in self.dependencies],
        }


class HealthService:
    def __init__(self, dependencies: list[DependencyHealthPort]) -> None:
        self._dependencies = dependencies

    async def liveness(self) -> dict[str, str]:
        return {"status": "ok"}

    async def readiness(self) -> HealthReport:
        statuses: list[DependencyStatus] = []
        for dependency in self._dependencies:
            status = await dependency.check()
            statuses.append(status)

        overall_status = "ok" if all(item.ok for item in statuses) else "degraded"
        return HealthReport(status=overall_status, dependencies=statuses)

