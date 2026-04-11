from fastapi.testclient import TestClient

from document_analyzer_api.domain.ports.health import DependencyStatus
from document_analyzer_api.main import create_app


class OkDependency:
    async def check(self) -> DependencyStatus:
        return DependencyStatus(name="stub", ok=True, detail="reachable")


class FailDependency:
    async def check(self) -> DependencyStatus:
        return DependencyStatus(name="stub", ok=False, detail="down")


def test_health_endpoint() -> None:
    app = create_app()
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers.get("X-Request-ID")


def test_ready_endpoint_ok() -> None:
    app = create_app()
    app.state.container.health_service._dependencies = [OkDependency()]

    with TestClient(app) as client:
        response = client.get("/api/v1/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ready_endpoint_degraded() -> None:
    app = create_app()
    app.state.container.health_service._dependencies = [FailDependency()]

    with TestClient(app) as client:
        response = client.get("/api/v1/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "degraded"


def test_metrics_endpoint_exposes_prometheus_format() -> None:
    app = create_app()

    with TestClient(app) as client:
        client.get("/api/v1/health")
        response = client.get("/api/v1/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "http_request_duration_ms_count" in response.text


