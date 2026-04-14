"""Module `tests/integration/test_real_mode_smoke.py`.

This module belongs to the project support layer of Document Analyzer.

Purpose:
- Implements a focused responsibility in the Document Analyzer codebase.

Defined symbols:
- Classes: none.
- Functions: _real_settings, test_real_mode_health_smoke, test_real_mode_end_to_end_flow.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import os

import pytest
from fastapi.testclient import TestClient

from document_analyzer_api.config.settings import Settings
from document_analyzer_api.main import create_app


RUN_REAL_E2E = os.getenv("RUN_REAL_E2E") == "1"


def _real_settings() -> Settings:
    """Synchronous execution path for `_real_settings`.
    
    This callable is implemented in `tests/integration/test_real_mode_smoke.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (Settings, getenv) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `Settings`.
    """
    return Settings(
        adapter_mode="real",
        mongodb_uri=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
        mongodb_database=os.getenv("MONGODB_DATABASE", "document_analyzer"),
        neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
        neo4j_password=os.getenv("NEO4J_PASSWORD", "neo4jpassword"),
        s3_endpoint=os.getenv("S3_ENDPOINT", "localhost:9000"),
        s3_access_key=os.getenv("S3_ACCESS_KEY", "minioadmin"),
        s3_secret_key=os.getenv("S3_SECRET_KEY", "minioadmin"),
        s3_bucket_raw=os.getenv("S3_BUCKET_RAW", "documents-raw"),
        s3_bucket_output=os.getenv("S3_BUCKET_OUTPUT", "documents-output"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_embedding_model=os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"),
        ollama_text_model=os.getenv("OLLAMA_TEXT_MODEL", "qwen3.5:9b"),
        tts_api_base_url=os.getenv("TTS_API_BASE_URL", "http://localhost:8010"),
        image_api_base_url=os.getenv("IMAGE_API_BASE_URL", "http://localhost:8002"),
        image_model=os.getenv("IMAGE_MODEL", "image-default"),
        default_tts_model=os.getenv("DEFAULT_TTS_MODEL", "Qwen/Qwen3-TTS-12Hz-0.6B-Base"),
        default_tts_voice=os.getenv("DEFAULT_TTS_VOICE", "alloy"),
    )


@pytest.mark.real_e2e
@pytest.mark.skipif(not RUN_REAL_E2E, reason="Set RUN_REAL_E2E=1 to run real-mode smoke tests")
def test_real_mode_health_smoke() -> None:
    """Synchronous execution path for `test_real_mode_health_smoke`.
    
    This callable is implemented in `tests/integration/test_real_mode_smoke.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (TestClient, _real_settings, create_app, get) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
    """
    app = create_app(_real_settings())
    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200


@pytest.mark.real_e2e
@pytest.mark.skipif(not RUN_REAL_E2E, reason="Set RUN_REAL_E2E=1 to run real-mode smoke tests")
def test_real_mode_end_to_end_flow() -> None:
    """Synchronous execution path for `test_real_mode_end_to_end_flow`.
    
    This callable is implemented in `tests/integration/test_real_mode_smoke.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (TestClient, _real_settings, create_app, delete) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
    """
    app = create_app(_real_settings())
    files = [("files", ("real_mode_book.txt", b"Hero enters the castle and defeats the dragon.", "text/plain"))]

    with TestClient(app) as client:
        ingest = client.post("/api/v1/documents", files=files)
        assert ingest.status_code in {200, 207}

        listed = client.get("/api/v1/documents")
        assert listed.status_code == 200

        generated = client.post(
            "/api/v1/documents/generate",
            json={
                "question": "Who defeats the dragon?",
                "stream": False,
                "includeSources": True,
                "retrievalOptions": {"common": {"minScore": 0.0}},
            },
        )
        assert generated.status_code == 200

        summary = client.post("/api/v1/documents/summary", json={"outputFormat": "md"})
        assert summary.status_code == 200

        session = client.post("/api/v1/chat/sessions")
        assert session.status_code == 200
        session_id = session.json()["sessionId"]

        chat = client.post(
            "/api/v1/documents/chat",
            json={
                "sessionId": session_id,
                "question": "Tell me what happened.",
                "stream": False,
                "retrievalOptions": {"common": {"minScore": 0.0}},
            },
        )
        assert chat.status_code == 200

        deleted = client.delete(f"/api/v1/chat/sessions/{session_id}")
        assert deleted.status_code in {200, 404}
