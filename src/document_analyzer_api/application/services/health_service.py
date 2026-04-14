"""Detailed module documentation for `src/document_analyzer_api/application/services/health_service.py`.

File role:
- Located in the application service layer.
- Defines logic and symbols for `health_service.py` within Document Analyzer V1.

Purpose:
- Implements use-case orchestration across domain ports and infrastructure adapters.

Exported symbols overview:
- Classes: HealthReport, HealthService.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from dataclasses import asdict, dataclass

from document_analyzer_api.domain.ports.health import DependencyHealthPort, DependencyStatus


@dataclass(slots=True)
class HealthReport:
    """Detailed class documentation for `HealthReport`.
    
    This component belongs to `src/document_analyzer_api/application/services/health_service.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    status: str
    dependencies: list[DependencyStatus]

    def to_dict(self) -> dict:
        """Detailed synchronous function documentation for `to_dict`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/health_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `to_dict` contract and consumed by downstream callers.
        """
        return {
            "status": self.status,
            "dependencies": [asdict(item) for item in self.dependencies],
        }


class HealthService:
    """Detailed class documentation for `HealthService`.
    
    This application service belongs to `src/document_analyzer_api/application/services/health_service.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, dependencies: list[DependencyHealthPort]) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/health_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                dependencies: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._dependencies = dependencies

    async def liveness(self) -> dict[str, str]:
        """Detailed asynchronous function documentation for `liveness`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/health_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `liveness` contract and consumed by downstream callers.
        """
        return {"status": "ok"}

    async def readiness(self) -> HealthReport:
        """Detailed asynchronous function documentation for `readiness`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/health_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `readiness` contract and consumed by downstream callers.
        """
        statuses: list[DependencyStatus] = []
        for dependency in self._dependencies:
            status = await dependency.check()
            statuses.append(status)

        overall_status = "ok" if all(item.ok for item in statuses) else "degraded"
        return HealthReport(status=overall_status, dependencies=statuses)

