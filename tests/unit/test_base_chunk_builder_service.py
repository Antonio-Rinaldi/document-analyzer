from document_analyzer_api.application.services.base_chunk_builder_service import BaseChunkBuilderService
from document_analyzer_api.domain.models.chunking import (
    ChunkGranularity,
    ChunkingConfig,
    ChunkingStrategyName,
    ParsedDocument,
    ParsedSection,
)


def test_build_chunks_paragraph_granularity() -> None:
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

