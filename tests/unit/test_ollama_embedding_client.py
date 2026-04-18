import asyncio

import httpx

from document_analyzer_api.infrastructure.embeddings.ollama_embedding_client import OllamaEmbeddingClient


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict, url: str) -> None:
        self.status_code = status_code
        self._payload = payload
        self._request = httpx.Request("POST", url)

    def json(self) -> dict:
        return self._payload

    @property
    def text(self) -> str:
        return str(self._payload)

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP {self.status_code}",
                request=self._request,
                response=httpx.Response(self.status_code, request=self._request),
            )


class _FakeAsyncClient:
    def __init__(self, responses: list[_FakeResponse], calls: list[str], timeout: float = 30.0) -> None:
        _ = timeout
        self._responses = responses
        self._calls = calls

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        _ = exc_type
        _ = exc
        _ = tb
        return False

    async def post(self, url: str, json: dict) -> _FakeResponse:
        _ = json
        self._calls.append(url)
        return self._responses.pop(0)


def test_embed_texts_uses_embeddings_api(monkeypatch) -> None:
    calls: list[str] = []
    responses = [
        _FakeResponse(
            200,
            {"embeddings": [[0.1, 0.2], [0.3, 0.4]]},
            "http://localhost:11434/api/embeddings",
        )
    ]

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda timeout=30.0, **kwargs: _FakeAsyncClient(responses, calls, timeout=timeout),
    )

    client = OllamaEmbeddingClient(base_url="http://localhost:11434", model="nomic-embed-text")
    vectors = asyncio.run(client.embed_texts(["a", "b"]))

    assert vectors == [[0.1, 0.2], [0.3, 0.4]]
    assert calls == ["http://localhost:11434/api/embeddings"]


def test_embed_texts_raises_runtime_error_with_response_body(monkeypatch) -> None:
    calls: list[str] = []
    responses = [
        _FakeResponse(404, {"error": "not found"}, "http://localhost:11434/api/embeddings"),
    ]

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda timeout=30.0, **kwargs: _FakeAsyncClient(responses, calls, timeout=timeout),
    )

    client = OllamaEmbeddingClient(base_url="http://localhost:11434", model="nomic-embed-text")
    try:
        asyncio.run(client.embed_texts(["first", "second"]))
    except RuntimeError as exc:
        message = str(exc)
        assert "/api/embeddings" in message
        assert "nomic-embed-text" in message
        assert "HTTP 404" in message
        assert calls == ["http://localhost:11434/api/embeddings"]
        return

    assert False, "Expected RuntimeError when /api/embeddings returns 404"


def test_embed_texts_raises_for_cardinality_mismatch(monkeypatch) -> None:
    """Fail fast when provider returns fewer vectors than requested texts."""
    calls: list[str] = []
    responses = [
        _FakeResponse(
            200,
            {"embeddings": [[0.1, 0.2]]},
            "http://localhost:11434/api/embeddings",
        )
    ]

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda timeout=30.0, **kwargs: _FakeAsyncClient(responses, calls, timeout=timeout),
    )

    client = OllamaEmbeddingClient(base_url="http://localhost:11434", model="nomic-embed-text")
    try:
        asyncio.run(client.embed_texts(["first", "second"]))
    except RuntimeError as exc:
        message = str(exc)
        assert "cardinality mismatch" in message
        assert "expected=2" in message
        assert "received=1" in message
        assert calls == ["http://localhost:11434/api/embeddings"]
        return

    assert False, "Expected RuntimeError for embeddings cardinality mismatch"


def test_embed_texts_raises_for_invalid_payload_shape(monkeypatch) -> None:
    """Fail fast when provider omits both `embeddings` and `embedding` payload forms."""
    calls: list[str] = []
    responses = [
        _FakeResponse(
            200,
            {"oops": "missing-embeddings"},
            "http://localhost:11434/api/embeddings",
        )
    ]

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda timeout=30.0, **kwargs: _FakeAsyncClient(responses, calls, timeout=timeout),
    )

    client = OllamaEmbeddingClient(base_url="http://localhost:11434", model="nomic-embed-text")
    try:
        asyncio.run(client.embed_texts(["first", "second"]))
    except RuntimeError as exc:
        message = str(exc)
        assert "did not contain a valid embeddings array" in message
        assert calls == ["http://localhost:11434/api/embeddings"]
        return

    assert False, "Expected RuntimeError for invalid embeddings payload shape"







