"""Module `tests/unit/test_base_chunk_builder_service.py`.

This module belongs to the project support layer of Document Analyzer.

Purpose:
- Implements a focused responsibility in the Document Analyzer codebase.

Defined symbols:
- Classes: none.
- Functions: test_build_chunks_paragraph_granularity, test_build_chunks_chapter_granularity, test_build_chunks_sub_paragraph_tokens.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from document_analyzer_api.application.services.base_chunk_builder_service import BaseChunkBuilderService
from document_analyzer_api.domain.models.chunking import (
    ChunkGranularity,
    ChunkingConfig,
    ChunkingStrategyName,
    ParsedDocument,
    ParsedSection,
)


def test_build_chunks_paragraph_granularity() -> None:
    """Synchronous execution path for `test_build_chunks_paragraph_granularity`.
    
    This callable is implemented in `tests/unit/test_base_chunk_builder_service.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (BaseChunkBuilderService, ChunkingConfig, ParsedDocument, ParsedSection) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
    """
    document = ParsedDocument(
        document_name="book.epub",
        sections=[
            ParsedSection(
                section_id="ch1",
                title="Chapter 1",
                text="Paragraph one.\n\nParagraph two.",
            )
        ],
    )
    service = BaseChunkBuilderService()

    chunks = service.build_chunks(
        document,
        ChunkingConfig(strategy=ChunkingStrategyName.meaningful, granularity=ChunkGranularity.paragraph),
    )

    assert len(chunks) == 2
    assert chunks[0].text == "Paragraph one."
    assert chunks[1].text == "Paragraph two."
    assert chunks[0].metadata["chapterId"] == "ch1"
    assert chunks[0].metadata["paragraphId"] == "ch1:p0"
    assert chunks[0].metadata["paragraphChunkIndex"] == 0
    assert chunks[1].metadata["paragraphId"] == "ch1:p1"
    assert chunks[1].metadata["paragraphChunkIndex"] == 0


def test_build_chunks_chapter_granularity() -> None:
    """Synchronous execution path for `test_build_chunks_chapter_granularity`.
    
    This callable is implemented in `tests/unit/test_base_chunk_builder_service.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (BaseChunkBuilderService, ChunkingConfig, ParsedDocument, ParsedSection) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
    """
    document = ParsedDocument(
        document_name="book.epub",
        sections=[ParsedSection(section_id="ch1", title="Chapter 1", text="Whole chapter text")],
    )
    service = BaseChunkBuilderService()

    chunks = service.build_chunks(
        document,
        ChunkingConfig(strategy=ChunkingStrategyName.meaningful, granularity=ChunkGranularity.chapter),
    )

    assert len(chunks) == 1
    assert chunks[0].text == "Whole chapter text"


def test_build_chunks_sub_paragraph_tokens() -> None:
    """Synchronous execution path for `test_build_chunks_sub_paragraph_tokens`.
    
    This callable is implemented in `tests/unit/test_base_chunk_builder_service.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (BaseChunkBuilderService, ChunkingConfig, ParsedDocument, ParsedSection) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
    """
    text = "one two three four five six seven eight nine ten"
    document = ParsedDocument(
        document_name="book.epub",
        sections=[ParsedSection(section_id="ch1", title="Chapter 1", text=text)],
    )
    service = BaseChunkBuilderService()

    chunks = service.build_chunks(
        document,
        ChunkingConfig(
            strategy=ChunkingStrategyName.meaningful,
            granularity=ChunkGranularity.sub_paragraph_tokens,
            target_tokens=4,
            overlap_tokens=1,
        ),
    )

    assert len(chunks) >= 3
    assert chunks[0].text == "one two three four"
    assert chunks[1].text.startswith("four five")
    assert chunks[0].metadata["paragraphChunkIndex"] == 0
    assert chunks[1].metadata["paragraphChunkIndex"] == 1

