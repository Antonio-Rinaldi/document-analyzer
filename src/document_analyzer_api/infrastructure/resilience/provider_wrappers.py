"""Module `src/document_analyzer_api/infrastructure/resilience/provider_wrappers.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: RetryEmbeddingClient, RetrySummarizer.
- Functions: _retry_async.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
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
    """Asynchronous execution path for `_retry_async`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/resilience/provider_wrappers.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (RuntimeError, operation, range, sleep) to satisfy the callable contract.
    
        Args:
            operation: Input parameter accepted by `_retry_async`.
            retries: Input parameter accepted by `_retry_async`.
            timeout_seconds: Input parameter accepted by `_retry_async`.
            backoff_seconds: Input parameter accepted by `_retry_async`.
    
        Returns:
            A value compatible with `Any`.
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
    """RetryEmbeddingClient component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/resilience/provider_wrappers.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(
        self,
        inner: EmbeddingClientPort,
        *,
        retries: int,
        timeout_seconds: float,
        backoff_seconds: float,
    ) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/resilience/provider_wrappers.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                inner: Input parameter accepted by `__init__`.
                retries: Input parameter accepted by `__init__`.
                timeout_seconds: Input parameter accepted by `__init__`.
                backoff_seconds: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._inner = inner
        self._retries = retries
        self._timeout_seconds = timeout_seconds
        self._backoff_seconds = backoff_seconds

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Asynchronous execution path for `embed_texts`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/resilience/provider_wrappers.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (_retry_async, embed_texts) to satisfy the callable contract.
        
            Args:
                texts: Input parameter accepted by `embed_texts`.
        
            Returns:
                A value compatible with `list[list[float]]`.
        """
        return await _retry_async(
            lambda: self._inner.embed_texts(texts),
            retries=self._retries,
            timeout_seconds=self._timeout_seconds,
            backoff_seconds=self._backoff_seconds,
        )


class RetrySummarizer(TextSummarizerPort):
    """RetrySummarizer component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/resilience/provider_wrappers.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(
        self,
        inner: TextSummarizerPort,
        *,
        retries: int,
        timeout_seconds: float,
        backoff_seconds: float,
    ) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/resilience/provider_wrappers.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                inner: Input parameter accepted by `__init__`.
                retries: Input parameter accepted by `__init__`.
                timeout_seconds: Input parameter accepted by `__init__`.
                backoff_seconds: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._inner = inner
        self._retries = retries
        self._timeout_seconds = timeout_seconds
        self._backoff_seconds = backoff_seconds

    async def summarize(self, target_text: str, context_text: str, prompt: str) -> str:
        """Asynchronous execution path for `summarize`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/resilience/provider_wrappers.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (_retry_async, summarize) to satisfy the callable contract.
        
            Args:
                target_text: Input parameter accepted by `summarize`.
                context_text: Input parameter accepted by `summarize`.
                prompt: Input parameter accepted by `summarize`.
        
            Returns:
                A value compatible with `str`.
        """
        return await _retry_async(
            lambda: self._inner.summarize(target_text=target_text, context_text=context_text, prompt=prompt),
            retries=self._retries,
            timeout_seconds=self._timeout_seconds,
            backoff_seconds=self._backoff_seconds,
        )

