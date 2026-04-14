"""Module `tests/unit/test_provider_wrappers.py`.

This module belongs to the project support layer of Document Analyzer.

Purpose:
- Implements a focused responsibility in the Document Analyzer codebase.

Defined symbols:
- Classes: FlakyEmbeddingClient, FlakySummarizer, SlowSummarizer.
- Functions: test_retry_embedding_client_retries_and_succeeds, test_retry_summarizer_retries_and_succeeds, test_retry_summarizer_times_out.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import asyncio

from document_analyzer_api.infrastructure.resilience.provider_wrappers import RetryEmbeddingClient, RetrySummarizer


class FlakyEmbeddingClient:
    """FlakyEmbeddingClient component.
    
    This class is defined in `tests/unit/test_provider_wrappers.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `tests/unit/test_provider_wrappers.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                None.
        
            Returns:
                A value compatible with `None`.
        """
        self.calls = 0

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Asynchronous execution path for `embed_texts`.
        
        This callable is implemented in `tests/unit/test_provider_wrappers.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (RuntimeError) to satisfy the callable contract.
        
            Args:
                texts: Input parameter accepted by `embed_texts`.
        
            Returns:
                A value compatible with `list[list[float]]`.
        """
        self.calls += 1
        if self.calls < 2:
            raise RuntimeError("temporary failure")
        return [[0.1] for _ in texts]


class FlakySummarizer:
    """FlakySummarizer component.
    
    This class is defined in `tests/unit/test_provider_wrappers.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `tests/unit/test_provider_wrappers.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                None.
        
            Returns:
                A value compatible with `None`.
        """
        self.calls = 0

    async def summarize(self, target_text: str, context_text: str, prompt: str) -> str:
        """Asynchronous execution path for `summarize`.
        
        This callable is implemented in `tests/unit/test_provider_wrappers.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (RuntimeError) to satisfy the callable contract.
        
            Args:
                target_text: Input parameter accepted by `summarize`.
                context_text: Input parameter accepted by `summarize`.
                prompt: Input parameter accepted by `summarize`.
        
            Returns:
                A value compatible with `str`.
        """
        self.calls += 1
        if self.calls < 2:
            raise RuntimeError("temporary failure")
        return f"{prompt}: {target_text[:10]}"


class SlowSummarizer:
    """SlowSummarizer component.
    
    This class is defined in `tests/unit/test_provider_wrappers.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    async def summarize(self, target_text: str, context_text: str, prompt: str) -> str:
        """Asynchronous execution path for `summarize`.
        
        This callable is implemented in `tests/unit/test_provider_wrappers.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (sleep) to satisfy the callable contract.
        
            Args:
                target_text: Input parameter accepted by `summarize`.
                context_text: Input parameter accepted by `summarize`.
                prompt: Input parameter accepted by `summarize`.
        
            Returns:
                A value compatible with `str`.
        """
        await asyncio.sleep(0.05)
        return target_text


def test_retry_embedding_client_retries_and_succeeds() -> None:
    """Synchronous execution path for `test_retry_embedding_client_retries_and_succeeds`.
    
    This callable is implemented in `tests/unit/test_provider_wrappers.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (FlakyEmbeddingClient, RetryEmbeddingClient, embed_texts, run) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
    """
    flaky = FlakyEmbeddingClient()
    client = RetryEmbeddingClient(flaky, retries=2, timeout_seconds=1.0, backoff_seconds=0.0)

    result = asyncio.run(client.embed_texts(["a", "b"]))

    assert flaky.calls == 2
    assert result == [[0.1], [0.1]]


def test_retry_summarizer_retries_and_succeeds() -> None:
    """Synchronous execution path for `test_retry_summarizer_retries_and_succeeds`.
    
    This callable is implemented in `tests/unit/test_provider_wrappers.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (FlakySummarizer, RetrySummarizer, run, startswith) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
    """
    flaky = FlakySummarizer()
    summarizer = RetrySummarizer(flaky, retries=2, timeout_seconds=1.0, backoff_seconds=0.0)

    result = asyncio.run(summarizer.summarize("target", "context", "prompt"))

    assert flaky.calls == 2
    assert result.startswith("prompt")


def test_retry_summarizer_times_out() -> None:
    """Synchronous execution path for `test_retry_summarizer_times_out`.
    
    This callable is implemented in `tests/unit/test_provider_wrappers.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (RetrySummarizer, SlowSummarizer, run, summarize) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
    """
    summarizer = RetrySummarizer(SlowSummarizer(), retries=0, timeout_seconds=0.001, backoff_seconds=0.0)

    try:
        asyncio.run(summarizer.summarize("target", "context", "prompt"))
    except TimeoutError:
        assert True
        return

    assert False, "Expected timeout"

