"""Module `tests/integration/test_health_endpoints.py`.

This module belongs to the project support layer of Document Analyzer.

Purpose:
- Implements a focused responsibility in the Document Analyzer codebase.

Defined symbols:
- Classes: OkDependency, FailDependency.
- Functions: test_health_endpoint, test_ready_endpoint_ok, test_ready_endpoint_degraded, test_metrics_endpoint_exposes_prometheus_format.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from fastapi.testclient import TestClient

from document_analyzer_api.domain.ports.health import DependencyStatus
from document_analyzer_api.main import create_app


class OkDependency:
    """OkDependency component.
    
    This class is defined in `tests/integration/test_health_endpoints.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    async def check(self) -> DependencyStatus:
        """Asynchronous execution path for `check`.
        
        This callable is implemented in `tests/integration/test_health_endpoints.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (DependencyStatus) to satisfy the callable contract.
        
            Args:
                None.
        
            Returns:
                A value compatible with `DependencyStatus`.
        """
        return DependencyStatus(name="stub", ok=True, detail="reachable")


class FailDependency:
    """FailDependency component.
    
    This class is defined in `tests/integration/test_health_endpoints.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    async def check(self) -> DependencyStatus:
        """Asynchronous execution path for `check`.
        
        This callable is implemented in `tests/integration/test_health_endpoints.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (DependencyStatus) to satisfy the callable contract.
        
            Args:
                None.
        
            Returns:
                A value compatible with `DependencyStatus`.
        """
        return DependencyStatus(name="stub", ok=False, detail="down")


def test_health_endpoint() -> None:
    """Synchronous execution path for `test_health_endpoint`.
    
    This callable is implemented in `tests/integration/test_health_endpoints.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (TestClient, create_app, get, json) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
    """
    app = create_app()
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers.get("X-Request-ID")


def test_ready_endpoint_ok() -> None:
    """Synchronous execution path for `test_ready_endpoint_ok`.
    
    This callable is implemented in `tests/integration/test_health_endpoints.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (OkDependency, TestClient, create_app, get) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
    """
    app = create_app()
    app.state.container.health_service._dependencies = [OkDependency()]

    with TestClient(app) as client:
        response = client.get("/api/v1/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ready_endpoint_degraded() -> None:
    """Synchronous execution path for `test_ready_endpoint_degraded`.
    
    This callable is implemented in `tests/integration/test_health_endpoints.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (FailDependency, TestClient, create_app, get) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
    """
    app = create_app()
    app.state.container.health_service._dependencies = [FailDependency()]

    with TestClient(app) as client:
        response = client.get("/api/v1/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "degraded"


def test_metrics_endpoint_exposes_prometheus_format() -> None:
    """Synchronous execution path for `test_metrics_endpoint_exposes_prometheus_format`.
    
    This callable is implemented in `tests/integration/test_health_endpoints.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (TestClient, create_app, get) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
    """
    app = create_app()

    with TestClient(app) as client:
        client.get("/api/v1/health")
        response = client.get("/api/v1/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "http_request_duration_ms_count" in response.text


