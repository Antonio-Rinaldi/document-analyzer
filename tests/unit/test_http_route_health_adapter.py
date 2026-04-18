import asyncio

import httpx

from document_analyzer_api.infrastructure.health.http_route_health_adapter import HttpRouteHealthAdapter


class _FakeResponse:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code


class _FakeAsyncClient:
    def __init__(self, responses: list[_FakeResponse], calls: list[tuple[str, dict]], timeout: float, **kwargs) -> None:
        _ = timeout
        _ = kwargs
        self._responses = responses
        self._calls = calls

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        _ = exc_type
        _ = exc
        _ = tb
        return False

    async def post(self, url: str, json: dict):
        await asyncio.sleep(0)
        self._calls.append((url, json))
        return self._responses.pop(0)

    async def get(self, url: str):
        await asyncio.sleep(0)
        self._calls.append((url, {}))
        return self._responses.pop(0)


def test_http_route_health_adapter_marks_non_404_client_error_as_up(monkeypatch) -> None:
    calls: list[tuple[str, dict]] = []
    responses = [_FakeResponse(422)]

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda timeout=2.0, **kwargs: _FakeAsyncClient(responses, calls, timeout=timeout, **kwargs),
    )

    adapter = HttpRouteHealthAdapter(
        name="tts_api",
        base_url="http://localhost:8000",
        path="/v1/audio/speech",
        timeout_seconds=2.0,
        payload={"model": "m", "voice": "v", "input": "ping"},
    )

    status = asyncio.run(adapter.check())

    assert status.ok is True
    assert status.name == "tts_api"
    assert calls == [("http://localhost:8000/v1/audio/speech", {"model": "m", "voice": "v", "input": "ping"})]


def test_http_route_health_adapter_marks_404_as_down(monkeypatch) -> None:
    responses = [_FakeResponse(404)]

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda timeout=2.0, **kwargs: _FakeAsyncClient(responses, [], timeout=timeout, **kwargs),
    )

    adapter = HttpRouteHealthAdapter(
        name="image_api",
        base_url="http://localhost:8002",
        path="/v1/images/generations",
        timeout_seconds=2.0,
        payload={"model": "m", "prompt": "ping"},
    )

    status = asyncio.run(adapter.check())

    assert status.ok is False
    assert status.name == "image_api"
    assert "route not found" in status.detail


def test_http_route_health_adapter_supports_get_method(monkeypatch) -> None:
    calls: list[tuple[str, dict]] = []
    responses = [_FakeResponse(200)]

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda timeout=2.0, **kwargs: _FakeAsyncClient(responses, calls, timeout=timeout, **kwargs),
    )

    adapter = HttpRouteHealthAdapter(
        name="tts_api",
        base_url="http://localhost:8000",
        path="/ready",
        timeout_seconds=2.0,
        method="GET",
    )

    status = asyncio.run(adapter.check())

    assert status.ok is True
    assert calls == [("http://localhost:8000/ready", {})]




