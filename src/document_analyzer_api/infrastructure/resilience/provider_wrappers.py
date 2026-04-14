"""Detailed module documentation for `src/document_analyzer_api/infrastructure/resilience/provider_wrappers.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `provider_wrappers.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: RetryEmbeddingClient, RetrySummarizer.
- Functions: _retry_async.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

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
    """Detailed asynchronous function documentation for `_retry_async`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/resilience/provider_wrappers.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            operation: Input parameter for `_retry_async`.
            retries: Input parameter for `_retry_async`.
            timeout_seconds: Input parameter for `_retry_async`.
            backoff_seconds: Input parameter for `_retry_async`.
    
        Returns:
            Value defined by `_retry_async` contract and consumed by downstream callers.
    """
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
    """Detailed class documentation for `RetryEmbeddingClient`.
    
    This component belongs to `src/document_analyzer_api/infrastructure/resilience/provider_wrappers.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(
        self,
        inner: EmbeddingClientPort,
        *,
        retries: int,
        timeout_seconds: float,
        backoff_seconds: float,
    ) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/resilience/provider_wrappers.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                inner: Input parameter for `__init__`.
                retries: Input parameter for `__init__`.
                timeout_seconds: Input parameter for `__init__`.
                backoff_seconds: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._inner = inner
        self._retries = retries
        self._timeout_seconds = timeout_seconds
        self._backoff_seconds = backoff_seconds

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Detailed asynchronous function documentation for `embed_texts`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/resilience/provider_wrappers.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                texts: Input parameter for `embed_texts`.
        
            Returns:
                Value defined by `embed_texts` contract and consumed by downstream callers.
        """
        return await _retry_async(
            lambda: self._inner.embed_texts(texts),
            retries=self._retries,
            timeout_seconds=self._timeout_seconds,
            backoff_seconds=self._backoff_seconds,
        )


class RetrySummarizer(TextSummarizerPort):
    """Detailed class documentation for `RetrySummarizer`.
    
    This component belongs to `src/document_analyzer_api/infrastructure/resilience/provider_wrappers.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(
        self,
        inner: TextSummarizerPort,
        *,
        retries: int,
        timeout_seconds: float,
        backoff_seconds: float,
    ) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/resilience/provider_wrappers.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                inner: Input parameter for `__init__`.
                retries: Input parameter for `__init__`.
                timeout_seconds: Input parameter for `__init__`.
                backoff_seconds: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._inner = inner
        self._retries = retries
        self._timeout_seconds = timeout_seconds
        self._backoff_seconds = backoff_seconds

    async def summarize(self, target_text: str, context_text: str, prompt: str) -> str:
        """Detailed asynchronous function documentation for `summarize`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/resilience/provider_wrappers.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                target_text: Input parameter for `summarize`.
                context_text: Input parameter for `summarize`.
                prompt: Input parameter for `summarize`.
        
            Returns:
                Value defined by `summarize` contract and consumed by downstream callers.
        """
        return await _retry_async(
            lambda: self._inner.summarize(target_text=target_text, context_text=context_text, prompt=prompt),
            retries=self._retries,
            timeout_seconds=self._timeout_seconds,
            backoff_seconds=self._backoff_seconds,
        )

