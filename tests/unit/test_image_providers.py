"""Validate resilient image provider behavior for unavailable upstream routes.

These tests lock runtime expectations for image modalities: provider-level HTTP failures
must return structured `image/unsupported` payloads so API generation/chat paths can
still return text answers without surfacing uncaught 500 errors.
"""

from __future__ import annotations

import httpx

from document_analyzer_api.domain.ports.image_provider import ImageProviderPort
from document_analyzer_api.infrastructure.modalities.http_image_provider import HttpImageProvider
from document_analyzer_api.infrastructure.modalities.ollama_image_provider import OllamaImageProvider


class _FakeSyncClient:
    """Minimal synchronous httpx client test double for image provider tests."""

    def __init__(self, response: httpx.Response) -> None:
        self._response = response

    def __enter__(self) -> "_FakeSyncClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        _ = exc_type
        _ = exc
        _ = tb
        return False

    def post(self, url: str, json: dict) -> httpx.Response:
        _ = json
        return httpx.Response(
            status_code=self._response.status_code,
            headers=self._response.headers,
            content=self._response.content,
            request=httpx.Request("POST", url),
        )


class _FailingFallback(ImageProviderPort):
    """Fallback provider test double that raises HTTP status failures."""

    def generate_from_text(self, text: str) -> dict:
        """Raise a deterministic HTTP status error consumed by resilience handling."""
        request = httpx.Request("POST", "http://fallback/v1/images/generations")
        response = httpx.Response(status_code=404, request=request)
        raise httpx.HTTPStatusError("fallback 404", request=request, response=response)


class _WorkingFallback(ImageProviderPort):
    """Fallback provider test double that returns a valid image payload."""

    def generate_from_text(self, text: str) -> dict:
        """Return a stable synthetic image payload for fallback success coverage."""
        return {"mimeType": "image/png", "dataBase64": "ZmFrZQ==", "promptUsed": text[:200]}


def test_http_image_provider_returns_unsupported_payload_on_404(monkeypatch) -> None:
    """Convert HTTP 404 upstream errors into non-raising image/unsupported payloads."""
    response = httpx.Response(status_code=404, request=httpx.Request("POST", "http://image/v1/images/generations"))
    monkeypatch.setattr(httpx, "Client", lambda timeout=60.0: _FakeSyncClient(response))

    provider = HttpImageProvider(base_url="http://image", model="image-model")

    payload = provider.generate_from_text("dragon scene")

    assert payload["mimeType"] == "image/unsupported"
    assert payload["provider"] == "http_image"
    assert "HTTP 404" in payload["warning"]


def test_ollama_image_provider_returns_unsupported_when_primary_and_fallback_fail(monkeypatch) -> None:
    """Avoid 500 propagation when both Ollama and fallback providers fail."""
    response = httpx.Response(status_code=404, request=httpx.Request("POST", "http://ollama/v1/images/generations"))
    monkeypatch.setattr(httpx, "Client", lambda timeout=60.0: _FakeSyncClient(response))

    provider = OllamaImageProvider(base_url="http://ollama", model="llava", fallback=_FailingFallback())

    payload = provider.generate_from_text("dragon scene")

    assert payload["mimeType"] == "image/unsupported"
    assert payload["provider"] == "ollama"
    assert "fallback=HTTPStatusError" in payload["warning"]


def test_ollama_image_provider_uses_fallback_payload_when_available(monkeypatch) -> None:
    """Keep image output available through fallback provider when Ollama route is missing."""
    response = httpx.Response(status_code=404, request=httpx.Request("POST", "http://ollama/v1/images/generations"))
    monkeypatch.setattr(httpx, "Client", lambda timeout=60.0: _FakeSyncClient(response))

    provider = OllamaImageProvider(base_url="http://ollama", model="llava", fallback=_WorkingFallback())

    payload = provider.generate_from_text("dragon scene")

    assert payload["mimeType"] == "image/png"
    assert payload["provider"] == "fallback"
    assert "Ollama image generation unavailable" in payload["warning"]

