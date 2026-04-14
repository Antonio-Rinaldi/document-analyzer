"""Detailed module documentation for `tests/unit/test_chunking_service.py`.

File role:
- Located in the project layer.
- Defines logic and symbols for `test_chunking_service.py` within Document Analyzer V1.

Purpose:
- Supports a focused concern in the Document Analyzer codebase.

Exported symbols overview:
- Classes: none.
- Functions: _sample_base_chunk, test_chunking_service_meaningful_keeps_text, test_chunking_service_contextual_summary_adds_source_excerpt.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

import asyncio

from document_analyzer_api.application.services.chunking_service import ChunkingService
from document_analyzer_api.domain.models.chunking import BaseChunk, ChunkingConfig, ChunkingStrategyName
from document_analyzer_api.infrastructure.chunking.deterministic_summarizer import DeterministicSummarizer


def _sample_base_chunk() -> BaseChunk:
    """Detailed synchronous function documentation for `_sample_base_chunk`.
    
    This callable is implemented in `tests/unit/test_chunking_service.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `_sample_base_chunk` contract and consumed by downstream callers.
    """
    return BaseChunk(
        chunk_id="ch1:0",
        section_id="ch1",
        text="This is a long paragraph that explains an idea clearly.",
        context_text="Full chapter context with extra details.",
        metadata={"granularity": "paragraph"},
    )


def test_chunking_service_meaningful_keeps_text() -> None:
    """Detailed synchronous function documentation for `test_chunking_service_meaningful_keeps_text`.
    
    This callable is implemented in `tests/unit/test_chunking_service.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `test_chunking_service_meaningful_keeps_text` contract and consumed by downstream callers.
    """
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
    """Detailed synchronous function documentation for `test_chunking_service_contextual_summary_adds_source_excerpt`.
    
    This callable is implemented in `tests/unit/test_chunking_service.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `test_chunking_service_contextual_summary_adds_source_excerpt` contract and consumed by downstream callers.
    """
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



