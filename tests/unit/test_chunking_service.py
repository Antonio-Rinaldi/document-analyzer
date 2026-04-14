"""Module `tests/unit/test_chunking_service.py`.

This module belongs to the project support layer of Document Analyzer.

Purpose:
- Implements a focused responsibility in the Document Analyzer codebase.

Defined symbols:
- Classes: none.
- Functions: _sample_base_chunk, test_chunking_service_meaningful_keeps_text, test_chunking_service_contextual_summary_adds_source_excerpt.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import asyncio

from document_analyzer_api.application.services.chunking_service import ChunkingService
from document_analyzer_api.domain.models.chunking import BaseChunk, ChunkingConfig, ChunkingStrategyName
from document_analyzer_api.infrastructure.chunking.deterministic_summarizer import DeterministicSummarizer


def _sample_base_chunk() -> BaseChunk:
    """Synchronous execution path for `_sample_base_chunk`.
    
    This callable is implemented in `tests/unit/test_chunking_service.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (BaseChunk) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `BaseChunk`.
    """
    return BaseChunk(
        chunk_id="ch1:0",
        section_id="ch1",
        text="This is a long paragraph that explains an idea clearly.",
        context_text="Full chapter context with extra details.",
        metadata={"granularity": "paragraph"},
    )


def test_chunking_service_meaningful_keeps_text() -> None:
    """Synchronous execution path for `test_chunking_service_meaningful_keeps_text`.
    
    This callable is implemented in `tests/unit/test_chunking_service.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (ChunkingConfig, ChunkingService, DeterministicSummarizer, _sample_base_chunk) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
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
    """Synchronous execution path for `test_chunking_service_contextual_summary_adds_source_excerpt`.
    
    This callable is implemented in `tests/unit/test_chunking_service.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (ChunkingConfig, ChunkingService, DeterministicSummarizer, _sample_base_chunk) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
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



