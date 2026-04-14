from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from document_analyzer_api.config.settings import Settings
from document_analyzer_api.main import create_app


def _make_app(tmp_path: Path) -> FastAPI:
    return create_app(Settings(storage_root_path=str(tmp_path)))


def test_list_documents_default_pagination(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    with TestClient(app) as client:
        response = client.get("/api/v1/documents")

    assert response.status_code == 200
    payload = response.json()
    assert payload["items"] == []
    assert payload["offset"] == 0
    assert payload["limit"] == 50
    assert payload["total"] == 0


def test_list_documents_invalid_offset_problem_details(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    with TestClient(app) as client:
        response = client.get("/api/v1/documents", params={"offset": -1})

    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/problem+json")
    payload = response.json()
    assert payload["errorCode"] == "REQUEST_VALIDATION_ERROR"


def test_documents_capabilities_returns_supported_formats(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    with TestClient(app) as client:
        response = client.get("/api/v1/documents/capabilities")

    assert response.status_code == 200
    payload = response.json()
    assert ".txt" in payload["supportedInputExtensions"]
    assert ".epub" in payload["supportedInputExtensions"]
    assert payload["supportedSummaryOutputFormats"] == ["md", "markdown", "txt"]


def test_ingest_documents_processed_then_already_processed(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    files = [("files", ("book.txt", b"dummy-content", "text/plain"))]

    with TestClient(app) as client:
        first = client.post("/api/v1/documents", files=files)
        second = client.post("/api/v1/documents", files=files)

    assert first.status_code == 200
    assert first.json()["results"][0]["status"] == "processed"
    assert first.json()["results"][0]["documentId"] is not None
    assert second.status_code == 200
    assert second.json()["results"][0]["status"] == "already_processed"


def test_ingest_documents_conflict_same_name_different_hash(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    files_v1 = [("files", ("book.txt", b"version-one", "text/plain"))]
    files_v2 = [("files", ("book.txt", b"version-two", "text/plain"))]

    with TestClient(app) as client:
        first = client.post("/api/v1/documents", files=files_v1)
        second = client.post("/api/v1/documents", files=files_v2)

    assert first.status_code == 200
    assert second.status_code == 207
    payload = second.json()
    assert payload["results"][0]["status"] == "conflict"
    assert payload["results"][0]["errorCode"] == "CONFLICT"


def test_ingest_documents_mixed_status_returns_207(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    files = [
        ("files", ("good.txt", b"ok", "text/plain")),
        ("files", ("bad.exe", b"nope", "application/octet-stream")),
    ]

    with TestClient(app) as client:
        response = client.post("/api/v1/documents", files=files)

    assert response.status_code == 207
    payload = response.json()
    statuses = [item["status"] for item in payload["results"]]
    assert statuses == ["processed", "unsupported_media_type"]


def test_ingest_documents_invalid_chunking_json(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    files = [("files", ("book.txt", b"dummy-content", "text/plain"))]
    data = {"chunking": "{not-json"}

    with TestClient(app) as client:
        response = client.post("/api/v1/documents", files=files, data=data)

    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/problem+json")
    payload = response.json()
    assert payload["errorCode"] == "VALIDATION_ERROR"


def test_ingest_documents_contextual_summary_custom_prompt_is_accepted(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    files = [("files", ("book.txt", b"dummy-content", "text/plain"))]
    data = {
        "chunking": '{"strategy":"contextual_summary","granularity":"paragraph",'
        '"strategyOptions":{"contextualSummary":{"prompt":"Only important happenings."}}}'
    }

    with TestClient(app) as client:
        response = client.post("/api/v1/documents", files=files, data=data)

    assert response.status_code == 200
    assert response.json()["results"][0]["status"] in {"processed", "already_processed"}


def test_list_documents_returns_processed_item(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    files = [("files", ("book.txt", b"chapter one\n\nchapter two", "text/plain"))]

    with TestClient(app) as client:
        ingest = client.post("/api/v1/documents", files=files)
        response = client.get("/api/v1/documents")

    assert ingest.status_code == 200
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["name"] == "book.txt"
    assert payload["items"][0]["description"]


def test_ingest_documents_contextual_summary_prompt_with_wrong_strategy_fails(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    files = [("files", ("book.txt", b"dummy-content", "text/plain"))]
    data = {
        "chunking": '{"strategy":"meaningful","granularity":"paragraph",'
        '"strategyOptions":{"contextualSummary":{"prompt":"Only important happenings."}}}'
    }

    with TestClient(app) as client:
        response = client.post("/api/v1/documents", files=files, data=data)

    assert response.status_code == 400
    assert response.json()["errorCode"] == "VALIDATION_ERROR"


def test_documents_summary_returns_local_url(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    files = [("files", ("book.txt", b"chapter one\n\nchapter two", "text/plain"))]

    with TestClient(app) as client:
        ingest = client.post("/api/v1/documents", files=files)
        response = client.post("/api/v1/documents/summary", json={"outputFormat": "md"})

    assert ingest.status_code == 200
    assert response.status_code == 200
    payload = response.json()
    assert payload["url"].startswith("local://output/")


def test_documents_generate_non_stream_returns_answer_and_citations(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    files = [(
        "files",
        ("book.txt", b"The hero enters the castle and fights the dragon.", "text/plain"),
    )]

    with TestClient(app) as client:
        ingest = client.post("/api/v1/documents", files=files)
        response = client.post(
            "/api/v1/documents/generate",
            json={
                "question": "Who fights the dragon?",
                "stream": False,
                "includeSources": True,
                "retrievalOptions": {"common": {"minScore": 0.0}},
            },
        )

    assert ingest.status_code == 200
    assert response.status_code == 200
    payload = response.json()
    assert "Based on selected documents:" in payload["answer"]
    assert payload["citations"]


def test_documents_generate_stream_returns_ollama_style_lines(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    files = [("files", ("book.txt", b"No overlap text.", "text/plain"))]

    with TestClient(app) as client:
        client.post("/api/v1/documents", files=files)
        response = client.post(
            "/api/v1/documents/generate",
            json={
                "question": "Unrelated query",
                "stream": True,
                "retrievalOptions": {"common": {"minScore": 1.0}},
            },
        )

    assert response.status_code == 200
    lines = [line for line in response.text.splitlines() if line.strip()]
    assert lines
    assert any('"done": true' in line for line in lines)


def test_chat_session_lifecycle_and_non_stream_chat(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    files = [(
        "files",
        ("book.txt", b"The hero enters the castle and fights the dragon.", "text/plain"),
    )]

    with TestClient(app) as client:
        client.post("/api/v1/documents", files=files)
        create = client.post("/api/v1/chat/sessions")
        session_id = create.json()["sessionId"]

        chat = client.post(
            "/api/v1/documents/chat",
            json={
                "sessionId": session_id,
                "question": "Who fights the dragon?",
                "stream": False,
                "includeSources": True,
                "retrievalOptions": {"common": {"minScore": 0.0}},
            },
        )
        delete = client.delete(f"/api/v1/chat/sessions/{session_id}")

    assert create.status_code == 200
    assert chat.status_code == 200
    assert chat.json()["sessionId"] == session_id
    assert chat.json()["answer"]
    assert delete.status_code == 200
    assert delete.json()["deleted"] is True


def test_chat_with_unknown_session_returns_validation_error(tmp_path: Path) -> None:
    app = _make_app(tmp_path)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/documents/chat",
            json={
                "sessionId": "missing-session",
                "question": "hello",
                "stream": False,
            },
        )

    assert response.status_code == 400
    assert response.json()["errorCode"] == "VALIDATION_ERROR"


def test_chat_stream_with_compact_context_flag(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    files = [("files", ("book.txt", b"Castle dragon hero story.", "text/plain"))]

    with TestClient(app) as client:
        client.post("/api/v1/documents", files=files)
        session_id = client.post("/api/v1/chat/sessions").json()["sessionId"]

        response = client.post(
            "/api/v1/documents/chat",
            json={
                "sessionId": session_id,
                "question": "Tell me what happens.",
                "stream": True,
                "compactContext": True,
                "retrievalOptions": {"common": {"minScore": 0.0}},
            },
        )

    assert response.status_code == 200
    lines = [line for line in response.text.splitlines() if line.strip()]
    assert lines
    assert any('"done": true' in line for line in lines)


def test_generate_audio_returns_wav_stream(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    files = [("files", ("book.txt", b"Hero fights dragon in castle.", "text/plain"))]

    with TestClient(app) as client:
        client.post("/api/v1/documents", files=files)
        response = client.post(
            "/api/v1/documents/generate",
            json={
                "question": "Who fights?",
                "outputFormat": "audio",
                "stream": False,
                "retrievalOptions": {"common": {"minScore": 0.0}},
            },
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/wav")
    assert len(response.content) > 44


def test_generate_image_returns_integrated_payload(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    files = [("files", ("book.txt", b"Hero fights dragon in castle.", "text/plain"))]

    with TestClient(app) as client:
        client.post("/api/v1/documents", files=files)
        response = client.post(
            "/api/v1/documents/generate",
            json={
                "question": "Show key scene",
                "outputFormat": "image",
                "stream": False,
                "retrievalOptions": {"common": {"minScore": 0.0}},
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"]
    assert payload["image"]["mimeType"] == "image/png"
    assert payload["image"]["dataBase64"]


def test_chat_audio_returns_binary_stream(tmp_path: Path) -> None:
    app = _make_app(tmp_path)
    files = [("files", ("book.txt", b"Hero fights dragon in castle.", "text/plain"))]

    with TestClient(app) as client:
        client.post("/api/v1/documents", files=files)
        session_id = client.post("/api/v1/chat/sessions").json()["sessionId"]
        response = client.post(
            "/api/v1/documents/chat",
            json={
                "sessionId": session_id,
                "question": "Who fights?",
                "outputFormat": "audio",
                "stream": False,
                "retrievalOptions": {"common": {"minScore": 0.0}},
            },
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/wav")
    assert len(response.content) > 44






