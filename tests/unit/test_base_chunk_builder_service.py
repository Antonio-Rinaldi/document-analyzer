"""Detailed module documentation for `tests/unit/test_base_chunk_builder_service.py`.

File role:
- Located in the project layer.
- Defines logic and symbols for `test_base_chunk_builder_service.py` within Document Analyzer V1.

Purpose:
- Supports a focused concern in the Document Analyzer codebase.

Exported symbols overview:
- Classes: none.
- Functions: test_build_chunks_paragraph_granularity, test_build_chunks_chapter_granularity, test_build_chunks_sub_paragraph_tokens.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
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
    """Detailed synchronous function documentation for `test_build_chunks_paragraph_granularity`.
    
    This callable is implemented in `tests/unit/test_base_chunk_builder_service.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `test_build_chunks_paragraph_granularity` contract and consumed by downstream callers.
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


def test_build_chunks_chapter_granularity() -> None:
    """Detailed synchronous function documentation for `test_build_chunks_chapter_granularity`.
    
    This callable is implemented in `tests/unit/test_base_chunk_builder_service.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `test_build_chunks_chapter_granularity` contract and consumed by downstream callers.
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
    """Detailed synchronous function documentation for `test_build_chunks_sub_paragraph_tokens`.
    
    This callable is implemented in `tests/unit/test_base_chunk_builder_service.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `test_build_chunks_sub_paragraph_tokens` contract and consumed by downstream callers.
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

