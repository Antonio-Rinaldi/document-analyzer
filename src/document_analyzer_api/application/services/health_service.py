"""Module `src/document_analyzer_api/application/services/health_service.py`.

This module belongs to the application service layer of Document Analyzer.

Purpose:
- Coordinates use-case workflows over domain ports and adapters.

Defined symbols:
- Classes: HealthReport, HealthService.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from dataclasses import asdict, dataclass

from document_analyzer_api.domain.ports.health import DependencyHealthPort, DependencyStatus


@dataclass(slots=True)
class HealthReport:
    """HealthReport component.
    
    This class is defined in `src/document_analyzer_api/application/services/health_service.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: status, dependencies.
    """
    status: str
    dependencies: list[DependencyStatus]

    def to_dict(self) -> dict:
        """Synchronous execution path for `to_dict`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/health_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (asdict) to satisfy the callable contract.
        
            Args:
                None.
        
            Returns:
                A value compatible with `dict`.
        """
        return {
            "status": self.status,
            "dependencies": [asdict(item) for item in self.dependencies],
        }


class HealthService:
    """HealthService application service.
    
    This class is defined in `src/document_analyzer_api/application/services/health_service.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, dependencies: list[DependencyHealthPort]) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/health_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                dependencies: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._dependencies = dependencies

    async def liveness(self) -> dict[str, str]:
        """Asynchronous execution path for `liveness`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/health_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                None.
        
            Returns:
                A value compatible with `dict[str, str]`.
        """
        return {"status": "ok"}

    async def readiness(self) -> HealthReport:
        """Asynchronous execution path for `readiness`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/health_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (HealthReport, all, append, check) to satisfy the callable contract.
        
            Args:
                None.
        
            Returns:
                A value compatible with `HealthReport`.
        """
        statuses: list[DependencyStatus] = []
        for dependency in self._dependencies:
            status = await dependency.check()
            statuses.append(status)

        overall_status = "ok" if all(item.ok for item in statuses) else "degraded"
        return HealthReport(status=overall_status, dependencies=statuses)

