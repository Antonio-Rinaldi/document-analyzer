import asyncio
from pathlib import Path

from document_analyzer_api.application.services.retrieval_service import RetrievalService
from document_analyzer_api.domain.models.persistence import PersistedChunk
from document_analyzer_api.domain.models.retrieval import KeywordsMode, RetrievalMode, RetrievalRequest
from document_analyzer_api.infrastructure.persistence.local_chunk_repository import LocalChunkRepository
from document_analyzer_api.infrastructure.retrieval.local_retrieval_backends import (
    LocalGraphRetrievalBackend,
    LocalHybridRetrievalBackend,
    LocalVectorRetrievalBackend,
)


def _seed_chunks(tmp_path: Path) -> None:
    chunks = [
        PersistedChunk(
            document_id="doc-1",
            chunk_id="section-0:0",
            content="The hero enters the castle and fights the dragon.",
            embedding=[0.1, 0.2],
            language="en",
            metadata={"sectionTitle": "Chapter 1", "keywords": ["hero", "dragon"]},
        ),
        PersistedChunk(
            document_id="doc-2",
            chunk_id="section-0:1",
            content="A cooking recipe with tomatoes and basil.",
            embedding=[0.2, 0.3],
            language="en",
            metadata={"sectionTitle": "Recipes", "keywords": ["cooking"]},
        ),
    ]

    async def _write() -> None:
        mongo = LocalChunkRepository(root_path=str(tmp_path), backend_name="mongo")
        neo4j = LocalChunkRepository(root_path=str(tmp_path), backend_name="neo4j")
        for repository in (mongo, neo4j):
            await repository.stage_chunks("doc-1", [chunks[0]], ttl_seconds=600)
            await repository.stage_chunks("doc-2", [chunks[1]], ttl_seconds=600)
            await repository.commit_document("doc-1")
            await repository.commit_document("doc-2")

    asyncio.run(_write())


def _build_service(tmp_path: Path) -> RetrievalService:
    return RetrievalService(
        vector_backend=LocalVectorRetrievalBackend(root_path=str(tmp_path)),
        graph_backend=LocalGraphRetrievalBackend(root_path=str(tmp_path)),
        hybrid_backend=LocalHybridRetrievalBackend(root_path=str(tmp_path)),
    )


def test_retrieval_modes_return_hits(tmp_path: Path) -> None:
    _seed_chunks(tmp_path)
    service = _build_service(tmp_path)

    for mode in (RetrievalMode.vector, RetrievalMode.graph, RetrievalMode.hybrid):
        result = asyncio.run(
            service.retrieve(
                RetrievalRequest(
                    query="hero dragon castle",
                    retrieval_mode=mode,
                    top_k=3,
                    min_score=0.0,
                )
            )
        )
        assert result.hits
        assert result.hits[0].document_id == "doc-1"


def test_keywords_filter_mode_respects_filtering(tmp_path: Path) -> None:
    _seed_chunks(tmp_path)
    service = _build_service(tmp_path)

    result = asyncio.run(
        service.retrieve(
            RetrievalRequest(
                query="recipe",
                retrieval_mode=RetrievalMode.vector,
                keywords=["dragon"],
                keywords_mode=KeywordsMode.filter,
                min_score=0.0,
            )
        )
    )

    assert all("dragon" in hit.content.lower() or "dragon" in str(hit.metadata).lower() for hit in result.hits)


def test_include_sources_returns_chunk_level_citations(tmp_path: Path) -> None:
    _seed_chunks(tmp_path)
    service = _build_service(tmp_path)

    result = asyncio.run(
        service.retrieve(
            RetrievalRequest(
                query="hero",
                retrieval_mode=RetrievalMode.vector,
                include_sources=True,
                min_score=0.0,
            )
        )
    )

    assert result.citations
    assert result.citations[0].chunk_id
    assert result.citations[0].document_id

