from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from ...domain.ports.embedding_client import EmbeddingClientPort
from ...domain.ports.text_summarizer import TextSummarizerPort


async def _retry_async(
    operation: Callable[[], Awaitable[Any]],
    *,
    retries: int,
    timeout_seconds: float,
    backoff_seconds: float,
) -> Any:
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return await asyncio.wait_for(operation(), timeout=timeout_seconds)
        except Exception as exc:
            last_exc = exc
            if attempt >= retries:
                break
            await asyncio.sleep(backoff_seconds * (attempt + 1))

    if last_exc is None:
        raise RuntimeError("Retry wrapper exhausted without exception")
    raise last_exc


class RetryEmbeddingClient(EmbeddingClientPort):
    def __init__(
        self,
        inner: EmbeddingClientPort,
        *,
        retries: int,
        timeout_seconds: float,
        backoff_seconds: float,
    ) -> None:
        self._inner = inner
        self._retries = retries
        self._timeout_seconds = timeout_seconds
        self._backoff_seconds = backoff_seconds

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return await _retry_async(
            lambda: self._inner.embed_texts(texts),
            retries=self._retries,
            timeout_seconds=self._timeout_seconds,
            backoff_seconds=self._backoff_seconds,
        )


class RetrySummarizer(TextSummarizerPort):
    def __init__(
        self,
        inner: TextSummarizerPort,
        *,
        retries: int,
        timeout_seconds: float,
        backoff_seconds: float,
    ) -> None:
        self._inner = inner
        self._retries = retries
        self._timeout_seconds = timeout_seconds
        self._backoff_seconds = backoff_seconds

    async def summarize(self, target_text: str, context_text: str, prompt: str) -> str:
        return await _retry_async(
            lambda: self._inner.summarize(target_text=target_text, context_text=context_text, prompt=prompt),
            retries=self._retries,
            timeout_seconds=self._timeout_seconds,
            backoff_seconds=self._backoff_seconds,
        )

