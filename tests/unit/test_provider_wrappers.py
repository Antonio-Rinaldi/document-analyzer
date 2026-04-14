"""Detailed module documentation for `tests/unit/test_provider_wrappers.py`.

File role:
- Located in the project layer.
- Defines logic and symbols for `test_provider_wrappers.py` within Document Analyzer V1.

Purpose:
- Supports a focused concern in the Document Analyzer codebase.

Exported symbols overview:
- Classes: FlakyEmbeddingClient, FlakySummarizer, SlowSummarizer.
- Functions: test_retry_embedding_client_retries_and_succeeds, test_retry_summarizer_retries_and_succeeds, test_retry_summarizer_times_out.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

import asyncio

from document_analyzer_api.infrastructure.resilience.provider_wrappers import RetryEmbeddingClient, RetrySummarizer


class FlakyEmbeddingClient:
    """Detailed class documentation for `FlakyEmbeddingClient`.
    
    This component belongs to `tests/unit/test_provider_wrappers.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `tests/unit/test_provider_wrappers.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self.calls = 0

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Detailed asynchronous function documentation for `embed_texts`.
        
        This callable is implemented in `tests/unit/test_provider_wrappers.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                texts: Input parameter for `embed_texts`.
        
            Returns:
                Value defined by `embed_texts` contract and consumed by downstream callers.
        """
        self.calls += 1
        if self.calls < 2:
            raise RuntimeError("temporary failure")
        return [[0.1] for _ in texts]


class FlakySummarizer:
    """Detailed class documentation for `FlakySummarizer`.
    
    This component belongs to `tests/unit/test_provider_wrappers.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `tests/unit/test_provider_wrappers.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self.calls = 0

    async def summarize(self, target_text: str, context_text: str, prompt: str) -> str:
        """Detailed asynchronous function documentation for `summarize`.
        
        This callable is implemented in `tests/unit/test_provider_wrappers.py` and contributes to the module workflow
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
        self.calls += 1
        if self.calls < 2:
            raise RuntimeError("temporary failure")
        return f"{prompt}: {target_text[:10]}"


class SlowSummarizer:
    """Detailed class documentation for `SlowSummarizer`.
    
    This component belongs to `tests/unit/test_provider_wrappers.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    async def summarize(self, target_text: str, context_text: str, prompt: str) -> str:
        """Detailed asynchronous function documentation for `summarize`.
        
        This callable is implemented in `tests/unit/test_provider_wrappers.py` and contributes to the module workflow
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
        await asyncio.sleep(0.05)
        return target_text


def test_retry_embedding_client_retries_and_succeeds() -> None:
    """Detailed synchronous function documentation for `test_retry_embedding_client_retries_and_succeeds`.
    
    This callable is implemented in `tests/unit/test_provider_wrappers.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `test_retry_embedding_client_retries_and_succeeds` contract and consumed by downstream callers.
    """
    flaky = FlakyEmbeddingClient()
    client = RetryEmbeddingClient(flaky, retries=2, timeout_seconds=1.0, backoff_seconds=0.0)

    result = asyncio.run(client.embed_texts(["a", "b"]))

    assert flaky.calls == 2
    assert result == [[0.1], [0.1]]


def test_retry_summarizer_retries_and_succeeds() -> None:
    """Detailed synchronous function documentation for `test_retry_summarizer_retries_and_succeeds`.
    
    This callable is implemented in `tests/unit/test_provider_wrappers.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `test_retry_summarizer_retries_and_succeeds` contract and consumed by downstream callers.
    """
    flaky = FlakySummarizer()
    summarizer = RetrySummarizer(flaky, retries=2, timeout_seconds=1.0, backoff_seconds=0.0)

    result = asyncio.run(summarizer.summarize("target", "context", "prompt"))

    assert flaky.calls == 2
    assert result.startswith("prompt")


def test_retry_summarizer_times_out() -> None:
    """Detailed synchronous function documentation for `test_retry_summarizer_times_out`.
    
    This callable is implemented in `tests/unit/test_provider_wrappers.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `test_retry_summarizer_times_out` contract and consumed by downstream callers.
    """
    summarizer = RetrySummarizer(SlowSummarizer(), retries=0, timeout_seconds=0.001, backoff_seconds=0.0)

    try:
        asyncio.run(summarizer.summarize("target", "context", "prompt"))
    except TimeoutError:
        assert True
        return

    assert False, "Expected timeout"

