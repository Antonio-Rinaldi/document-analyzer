"""Detailed module documentation for `tests/integration/test_health_endpoints.py`.

File role:
- Located in the project layer.
- Defines logic and symbols for `test_health_endpoints.py` within Document Analyzer V1.

Purpose:
- Supports a focused concern in the Document Analyzer codebase.

Exported symbols overview:
- Classes: OkDependency, FailDependency.
- Functions: test_health_endpoint, test_ready_endpoint_ok, test_ready_endpoint_degraded, test_metrics_endpoint_exposes_prometheus_format.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from fastapi.testclient import TestClient

from document_analyzer_api.domain.ports.health import DependencyStatus
from document_analyzer_api.main import create_app


class OkDependency:
    """Detailed class documentation for `OkDependency`.
    
    This component belongs to `tests/integration/test_health_endpoints.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    async def check(self) -> DependencyStatus:
        """Detailed asynchronous function documentation for `check`.
        
        This callable is implemented in `tests/integration/test_health_endpoints.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `check` contract and consumed by downstream callers.
        """
        return DependencyStatus(name="stub", ok=True, detail="reachable")


class FailDependency:
    """Detailed class documentation for `FailDependency`.
    
    This component belongs to `tests/integration/test_health_endpoints.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    async def check(self) -> DependencyStatus:
        """Detailed asynchronous function documentation for `check`.
        
        This callable is implemented in `tests/integration/test_health_endpoints.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `check` contract and consumed by downstream callers.
        """
        return DependencyStatus(name="stub", ok=False, detail="down")


def test_health_endpoint() -> None:
    """Detailed synchronous function documentation for `test_health_endpoint`.
    
    This callable is implemented in `tests/integration/test_health_endpoints.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `test_health_endpoint` contract and consumed by downstream callers.
    """
    app = create_app()
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers.get("X-Request-ID")


def test_ready_endpoint_ok() -> None:
    """Detailed synchronous function documentation for `test_ready_endpoint_ok`.
    
    This callable is implemented in `tests/integration/test_health_endpoints.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `test_ready_endpoint_ok` contract and consumed by downstream callers.
    """
    app = create_app()
    app.state.container.health_service._dependencies = [OkDependency()]

    with TestClient(app) as client:
        response = client.get("/api/v1/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ready_endpoint_degraded() -> None:
    """Detailed synchronous function documentation for `test_ready_endpoint_degraded`.
    
    This callable is implemented in `tests/integration/test_health_endpoints.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `test_ready_endpoint_degraded` contract and consumed by downstream callers.
    """
    app = create_app()
    app.state.container.health_service._dependencies = [FailDependency()]

    with TestClient(app) as client:
        response = client.get("/api/v1/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "degraded"


def test_metrics_endpoint_exposes_prometheus_format() -> None:
    """Detailed synchronous function documentation for `test_metrics_endpoint_exposes_prometheus_format`.
    
    This callable is implemented in `tests/integration/test_health_endpoints.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `test_metrics_endpoint_exposes_prometheus_format` contract and consumed by downstream callers.
    """
    app = create_app()

    with TestClient(app) as client:
        client.get("/api/v1/health")
        response = client.get("/api/v1/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "http_request_duration_ms_count" in response.text


