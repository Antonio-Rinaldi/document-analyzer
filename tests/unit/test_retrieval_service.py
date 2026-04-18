"""Module `tests/unit/test_retrieval_service.py`.

This module belongs to the project support layer of Document Analyzer.

Purpose:
- Implements a focused responsibility in the Document Analyzer codebase.

Defined symbols:
- Classes: none.
- Functions: _seed_chunks, _build_service, test_retrieval_modes_return_hits, test_keywords_filter_mode_respects_filtering, test_include_sources_returns_chunk_level_citations.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

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
    _graphish_connectivity_bonus,
)


def _seed_chunks(tmp_path: Path) -> None:
    """Synchronous execution path for `_seed_chunks`.
    
    This callable is implemented in `tests/unit/test_retrieval_service.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (LocalChunkRepository, PersistedChunk, _write, commit_document) to satisfy the callable contract.
    
        Args:
            tmp_path: Input parameter accepted by `_seed_chunks`.
    
        Returns:
            A value compatible with `None`.
    """
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
        """Asynchronous execution path for `_write`.
        
        This callable is implemented in `tests/unit/test_retrieval_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (LocalChunkRepository, commit_document, stage_chunks, str) to satisfy the callable contract.
        
            Args:
                None.
        
            Returns:
                A value compatible with `None`.
        """
        mongo = LocalChunkRepository(root_path=str(tmp_path), backend_name="mongo")
        neo4j = LocalChunkRepository(root_path=str(tmp_path), backend_name="neo4j")
        for repository in (mongo, neo4j):
            await repository.stage_chunks("doc-1", [chunks[0]], ttl_seconds=600)
            await repository.stage_chunks("doc-2", [chunks[1]], ttl_seconds=600)
            await repository.commit_document("doc-1")
            await repository.commit_document("doc-2")

    asyncio.run(_write())


def _build_service(tmp_path: Path) -> RetrievalService:
    """Synchronous execution path for `_build_service`.
    
    This callable is implemented in `tests/unit/test_retrieval_service.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (LocalGraphRetrievalBackend, LocalHybridRetrievalBackend, LocalVectorRetrievalBackend, RetrievalService) to satisfy the callable contract.
    
        Args:
            tmp_path: Input parameter accepted by `_build_service`.
    
        Returns:
            A value compatible with `RetrievalService`.
    """
    return RetrievalService(
        vector_backend=LocalVectorRetrievalBackend(root_path=str(tmp_path)),
        graph_backend=LocalGraphRetrievalBackend(root_path=str(tmp_path)),
        hybrid_backend=LocalHybridRetrievalBackend(root_path=str(tmp_path)),
    )


def test_retrieval_modes_return_hits(tmp_path: Path) -> None:
    """Synchronous execution path for `test_retrieval_modes_return_hits`.
    
    This callable is implemented in `tests/unit/test_retrieval_service.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (RetrievalRequest, _build_service, _seed_chunks, retrieve) to satisfy the callable contract.
    
        Args:
            tmp_path: Input parameter accepted by `test_retrieval_modes_return_hits`.
    
        Returns:
            A value compatible with `None`.
    """
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
    """Synchronous execution path for `test_keywords_filter_mode_respects_filtering`.
    
    This callable is implemented in `tests/unit/test_retrieval_service.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (RetrievalRequest, _build_service, _seed_chunks, all) to satisfy the callable contract.
    
        Args:
            tmp_path: Input parameter accepted by `test_keywords_filter_mode_respects_filtering`.
    
        Returns:
            A value compatible with `None`.
    """
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
    """Synchronous execution path for `test_include_sources_returns_chunk_level_citations`.
    
    This callable is implemented in `tests/unit/test_retrieval_service.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (RetrievalRequest, _build_service, _seed_chunks, retrieve) to satisfy the callable contract.
    
        Args:
            tmp_path: Input parameter accepted by `test_include_sources_returns_chunk_level_citations`.
    
        Returns:
            A value compatible with `None`.
    """
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


def test_graphish_connectivity_bonus_uses_connections_paths_and_depth() -> None:
    """Weight graph metadata using neighbor count, path count, and inverse minimum depth."""
    bonus = _graphish_connectivity_bonus(
        {
            "connections": ["c1", "c2", "c3"],
            "graphPathCount": 6,
            "graphMinDepth": 2,
        }
    )

    assert bonus > 0.0
    assert round(bonus, 2) == 6.50


