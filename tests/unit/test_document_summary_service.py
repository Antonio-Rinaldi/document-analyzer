"""Validate RAG-backed summary orchestration behavior.

These tests ensure `/documents/summary` uses retrieval evidence plus text generation
instead of static metadata concatenation.
"""

from __future__ import annotations

import asyncio

from document_analyzer_api.application.services.document_summary_service import (
    INSUFFICIENT_EVIDENCE_MESSAGE,
    DocumentSummaryService,
)
from document_analyzer_api.domain.models.retrieval import RetrievalHit, RetrievalResult
from document_analyzer_api.domain.ports.document_creator import CreatedDocument


class _StubRetrievalService:
    """Return deterministic retrieval results while capturing request parameters."""

    def __init__(self, *, hits: list[RetrievalHit]) -> None:
        self._hits = hits
        self.last_request = None

    async def retrieve(self, request):  # type: ignore[no-untyped-def]
        """Store request and return configured retrieval hits."""
        await asyncio.sleep(0)
        self.last_request = request
        return RetrievalResult(hits=self._hits, citations=[])


class _StubTextGenerationClient:
    """Return deterministic generated text while capturing question and context."""

    def __init__(self) -> None:
        self.last_question = ""
        self.last_context: list[str] = []

    async def generate_answer(self, question: str, context_chunks: list[str]) -> str:
        """Store generation inputs and return synthetic summary text."""
        await asyncio.sleep(0)
        self.last_question = question
        self.last_context = context_chunks
        return "Generated summary from retrieval evidence"


class _StubDocumentCreator:
    """Create deterministic summary output payloads."""

    def supported_output_formats(self) -> tuple[str, ...]:
        """Expose supported output formats used by summary route validation."""
        return ("md", "markdown", "txt")

    async def create(self, *, summary_text: str, output_format: str, filename_stem: str) -> CreatedDocument:
        """Return generated content without mutating summary text."""
        await asyncio.sleep(0)
        extension = "txt" if output_format == "txt" else "md"
        return CreatedDocument(filename=f"{filename_stem}.{extension}", content=summary_text.encode("utf-8"))


class _StubOutputStorage:
    """Capture output writes and return a local URL."""

    def __init__(self) -> None:
        self.last_filename = ""
        self.last_content = b""
        self.last_content_type = ""

    async def write_output(self, filename: str, content: bytes, content_type: str | None = None) -> str:
        """Store output write payload and return deterministic locator."""
        await asyncio.sleep(0)
        self.last_filename = filename
        self.last_content = content
        self.last_content_type = content_type or ""
        return f"local://output/{filename}"


def test_create_summary_uses_retrieval_and_generation() -> None:
    """Create summary from retrieval evidence and pass generated text to output storage."""
    retrieval = _StubRetrievalService(
        hits=[
            RetrievalHit(document_id="doc-1", chunk_id="c1", content="hero enters castle", score=0.9, metadata={}),
            RetrievalHit(document_id="doc-1", chunk_id="c2", content="dragon battle", score=0.8, metadata={}),
        ]
    )
    generator = _StubTextGenerationClient()
    creator = _StubDocumentCreator()
    output = _StubOutputStorage()
    service = DocumentSummaryService(
        retrieval_service=retrieval,
        text_generation_client=generator,
        output_storage=output,
        document_creator=creator,
    )

    url, summary_text = asyncio.run(
        service.create_summary(
            document_ids=None,
            keywords=["plot summary", "main characters"],
            keywords_mode="rank_boost",
            retrieval_mode="graph",
            top_k=5,
            min_score=0.0,
            hybrid_alpha=0.4,
            graph_max_hops=3,
            summary_word_count=220,
            summary_prompt="Write in Wikipedia style with neutral tone.",
            output_format="md",
        )
    )

    assert url.startswith("local://output/summary-")
    assert retrieval.last_request is not None
    assert retrieval.last_request.retrieval_mode.value == "graph"
    assert retrieval.last_request.graph_max_hops == 3
    assert generator.last_context == ["hero enters castle", "dragon battle"]
    assert "Focus on: plot summary, main characters." in generator.last_question
    assert "Target length: approximately 220 words." in generator.last_question
    assert "Additional instruction: Write in Wikipedia style with neutral tone." in generator.last_question
    assert summary_text == "Generated summary from retrieval evidence"
    assert output.last_content.decode("utf-8") == "Generated summary from retrieval evidence"


def test_create_summary_returns_insufficient_evidence_when_no_hits() -> None:
    """Persist strict insufficient-evidence message when retrieval yields no context chunks."""
    retrieval = _StubRetrievalService(hits=[])
    generator = _StubTextGenerationClient()
    creator = _StubDocumentCreator()
    output = _StubOutputStorage()
    service = DocumentSummaryService(
        retrieval_service=retrieval,
        text_generation_client=generator,
        output_storage=output,
        document_creator=creator,
    )

    _, summary_text = asyncio.run(
        service.create_summary(
            document_ids=["doc-404"],
            keywords=[],
            keywords_mode="metadata_only",
            retrieval_mode="vector",
            top_k=8,
            min_score=1.0,
            hybrid_alpha=0.5,
            graph_max_hops=2,
            summary_word_count=None,
            summary_prompt=None,
            output_format="txt",
        )
    )

    assert generator.last_context == []
    assert summary_text == INSUFFICIENT_EVIDENCE_MESSAGE
    assert output.last_content.decode("utf-8") == INSUFFICIENT_EVIDENCE_MESSAGE





