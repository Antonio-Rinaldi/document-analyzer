import asyncio

from document_analyzer_api.application.services.chunking_service import ChunkingService
from document_analyzer_api.domain.models.chunking import BaseChunk, ChunkingConfig, ChunkingStrategyName
from document_analyzer_api.infrastructure.chunking.deterministic_summarizer import DeterministicSummarizer


def _sample_base_chunk() -> BaseChunk:
    return BaseChunk(
        chunk_id="ch1:0",
        section_id="ch1",
        text="This is a long paragraph that explains an idea clearly.",
        context_text="Full chapter context with extra details.",
        metadata={"granularity": "paragraph"},
    )


def test_chunking_service_meaningful_keeps_text() -> None:
    service = ChunkingService(summarizer=DeterministicSummarizer())
    chunk = _sample_base_chunk()

    result = asyncio.run(
        service.apply_strategy(
            [chunk],
            ChunkingConfig(strategy=ChunkingStrategyName.meaningful),
        )
    )

    assert len(result) == 1
    assert result[0].content == chunk.text


def test_chunking_service_contextual_summary_adds_source_excerpt() -> None:
    service = ChunkingService(summarizer=DeterministicSummarizer())
    chunk = _sample_base_chunk()

    result = asyncio.run(
        service.apply_strategy(
            [chunk],
            ChunkingConfig(
                strategy=ChunkingStrategyName.contextual_summary,
                contextual_summary_prompt="Only important happenings.",
            ),
        )
    )

    assert len(result) == 1
    assert result[0].content.startswith("[Only important happenings.]")
    assert result[0].metadata["sourceExcerpt"].startswith("This is a long paragraph")



