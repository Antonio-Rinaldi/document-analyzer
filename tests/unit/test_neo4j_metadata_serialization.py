"""Validate Neo4j metadata serialization boundaries for chunk persistence and retrieval.

These tests lock the contract introduced for Neo4j persistence: chunk metadata can contain
nested dictionaries/lists in Python, but Neo4j properties cannot store maps directly. The
persistence adapter therefore serializes metadata as JSON, and the retrieval adapter decodes
that JSON back into dictionaries before ranking/citation logic consumes the records.
"""

from types import SimpleNamespace

from document_analyzer_api.infrastructure.persistence.neo4j_chunk_repository import Neo4jChunkRepository
from document_analyzer_api.infrastructure.retrieval.neo4j_graph_retrieval_backend import Neo4jGraphRetrievalBackend
from document_analyzer_api.domain.models.persistence import PersistedChunk


def test_serialize_metadata_produces_json_string_for_nested_metadata() -> None:
    """Ensure nested metadata is transformed into a Neo4j-safe JSON property value."""
    metadata = {
        "chunkGranularity": "paragraph",
        "nested": {"sectionTitle": "FOR", "offset": 12},
        "tags": ["epub", "chapter"],
    }

    serialized = Neo4jChunkRepository._serialize_metadata(metadata)

    assert isinstance(serialized, str)
    assert '"chunkGranularity":"paragraph"' in serialized
    assert '"nested":{"sectionTitle":"FOR","offset":12}' in serialized


def test_decode_metadata_reads_metadata_json_payload() -> None:
    """Decode metadataJson into the dictionary shape expected by retrieval ranking code."""
    payload = '{"chunkingStrategy":"meaningful","granularity":"paragraph"}'

    decoded = Neo4jGraphRetrievalBackend._decode_metadata(payload)

    assert decoded == {"chunkingStrategy": "meaningful", "granularity": "paragraph"}


def test_decode_metadata_returns_empty_dict_for_invalid_json() -> None:
    """Guard retrieval flow against malformed persisted metadata strings."""
    decoded = Neo4jGraphRetrievalBackend._decode_metadata("{not-json}")

    assert decoded == {}


def test_extract_hierarchy_uses_metadata_identifiers() -> None:
    """Resolve hierarchy node IDs from chunk metadata when fields are present."""
    chunk = PersistedChunk(
        document_id="doc-1",
        chunk_id="section-7:3",
        content="content",
        embedding=[0.1],
        language="en",
        metadata={
            "chapterId": "chapter-7",
            "chapterTitle": "Battle",
            "chapterIndex": 7,
            "paragraphId": "chapter-7:p2",
            "paragraphIndex": 2,
            "paragraphChunkIndex": 3,
        },
    )

    hierarchy = Neo4jChunkRepository._extract_hierarchy(chunk)

    assert hierarchy["chapter_id"] == "chapter-7"
    assert hierarchy["chapter_title"] == "Battle"
    assert hierarchy["paragraph_id"] == "chapter-7:p2"
    assert hierarchy["paragraph_index"] == 2
    assert hierarchy["paragraph_chunk_index"] == 3


def test_merge_graph_metadata_adds_connections_and_hierarchy_defaults() -> None:
    """Inject traversal payload into metadata consumed by graph ranking."""

    class _Row:
        def get(self, key: str, default: object = None) -> object:
            row = {
                "connections": ["chunk-2", "chunk-3", 5],
                "graph_path_count": 4,
                "graph_min_depth": 2,
                "chapter_id": "chapter-1",
                "chapter_title": "Chapter One",
                "paragraph_id": "chapter-1:p0",
                "paragraph_index": 0,
            }
            return row.get(key, default)

    merged = Neo4jGraphRetrievalBackend._merge_graph_metadata(metadata={}, row=_Row())

    assert merged["connections"] == ["chunk-2", "chunk-3"]
    assert merged["graphPathCount"] == 4
    assert merged["graphMinDepth"] == 2
    assert merged["chapterId"] == "chapter-1"
    assert merged["sectionTitle"] == "Chapter One"


def test_build_committed_query_uses_literal_hop_range() -> None:
    """Ensure graph traversal depth is rendered as Cypher literal, not as parameter syntax."""
    query = Neo4jGraphRetrievalBackend._build_committed_chunks_query(3)

    assert "*1..3" in query
    assert "*1..$max_hops" not in query


def test_normalize_graph_hops_clamps_to_supported_range() -> None:
    """Keep graph traversal settings safe and compatible with Neo4j variable-length syntax."""
    assert Neo4jGraphRetrievalBackend._normalize_graph_hops(0) == 1
    assert Neo4jGraphRetrievalBackend._normalize_graph_hops(5) == 5
    assert Neo4jGraphRetrievalBackend._normalize_graph_hops(999) == 32


def test_read_committed_uses_hop_literal_query_without_cypher_parameters() -> None:
    """Execute graph read path with a fake session and validate no parameter map is sent."""

    class _Session:
        def __init__(self) -> None:
            self.query = ""
            self.params = None

        def __enter__(self) -> "_Session":
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def run(self, query: str, **params: object) -> list[dict[str, object]]:
            self.query = query
            self.params = params
            return []

    class _Driver:
        def __init__(self) -> None:
            self.last_session = _Session()

        def session(self) -> _Session:
            return self.last_session

    backend = Neo4jGraphRetrievalBackend.__new__(Neo4jGraphRetrievalBackend)
    backend._driver = _Driver()

    records = backend._read_committed(SimpleNamespace(graph_max_hops=3))

    assert records == []
    assert "*1..3" in backend._driver.last_session.query
    assert backend._driver.last_session.params == {}


