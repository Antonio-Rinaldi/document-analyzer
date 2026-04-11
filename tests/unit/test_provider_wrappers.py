import asyncio

from document_analyzer_api.infrastructure.resilience.provider_wrappers import RetryEmbeddingClient, RetrySummarizer


class FlakyEmbeddingClient:
    def __init__(self) -> None:
        self.calls = 0

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self.calls += 1
        if self.calls < 2:
            raise RuntimeError("temporary failure")
        return [[0.1] for _ in texts]


class FlakySummarizer:
    def __init__(self) -> None:
        self.calls = 0

    async def summarize(self, target_text: str, context_text: str, prompt: str) -> str:
        self.calls += 1
        if self.calls < 2:
            raise RuntimeError("temporary failure")
        return f"{prompt}: {target_text[:10]}"


class SlowSummarizer:
    async def summarize(self, target_text: str, context_text: str, prompt: str) -> str:
        await asyncio.sleep(0.05)
        return target_text


def test_retry_embedding_client_retries_and_succeeds() -> None:
    flaky = FlakyEmbeddingClient()
    client = RetryEmbeddingClient(flaky, retries=2, timeout_seconds=1.0, backoff_seconds=0.0)

    result = asyncio.run(client.embed_texts(["a", "b"]))

    assert flaky.calls == 2
    assert result == [[0.1], [0.1]]


def test_retry_summarizer_retries_and_succeeds() -> None:
    flaky = FlakySummarizer()
    summarizer = RetrySummarizer(flaky, retries=2, timeout_seconds=1.0, backoff_seconds=0.0)

    result = asyncio.run(summarizer.summarize("target", "context", "prompt"))

    assert flaky.calls == 2
    assert result.startswith("prompt")


def test_retry_summarizer_times_out() -> None:
    summarizer = RetrySummarizer(SlowSummarizer(), retries=0, timeout_seconds=0.001, backoff_seconds=0.0)

    try:
        asyncio.run(summarizer.summarize("target", "context", "prompt"))
    except TimeoutError:
        assert True
        return

    assert False, "Expected timeout"

