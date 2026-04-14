# document-analyzer

Internal RAG API (FastAPI) for document ingestion, dual-store retrieval (MongoDB + Neo4j), and multimodal generation.

## What This Service Does

- Exposes versioned endpoints under `/api/v1`.
- Ingests documents with `POST /api/v1/documents`.
- Parses incoming files with Microsoft MarkItDown and builds chunked RAG data.
- Persists processed chunks in both MongoDB and Neo4j.
- Supports retrieval modes `vector`, `graph`, and `hybrid`.
- Supports generate, summary, and chat workflows.
- Supports text, audio, image, and text+image responses.

## Architecture And Design Choices

The service follows clean architecture with explicit ports/adapters:

- **Facade services**: `DocumentIngestionService`, `DocumentGenerationService`, `DocumentSummaryService`, `ChatService`.
- **Ports and adapters**: storage, parser, creator, retrieval backends, and AI providers are isolated behind interfaces.
- **Strategy**: retrieval mode (`vector` / `graph` / `hybrid`) is selected per request.
- **Pipeline**: ingestion flow is parse -> chunk -> transform -> embed -> persist.
- **Fail-fast config**: `Settings.validate_runtime()` validates adapter mode and required real-mode env.
- **Dependency injection**: composition is centralized in `bootstrap/container.py`.

## Document Processing Pipeline

### 1) Ingestion

Implemented in `src/document_analyzer_api/api/routes/documents.py` and `application/services/document_ingestion_service.py`:

- validates multipart request limits (count/size/total payload)
- validates extension against MarkItDown-supported inputs
- enforces duplicate-name idempotency with hash + `.done` semantics
- supports per-file partial outcomes (`200` all ok, `207` mixed)

### 2) Parsing + Chunking

Implemented in `infrastructure/parsing/markitdown_document_parser.py` and chunking services:

- parses supported file types through MarkItDown into normalized text
- keeps section-aware structure for downstream chunking
- supports chunking strategy selection:
  - `meaningful`
  - `contextual_summary` (with optional custom prompt criteria)

### 3) Persistence + Retrieval

- stages chunk writes with TTL and commits only on full-file success
- writes chunks to MongoDB and Neo4j
- supports retrieval modes:
  - `vector`
  - `graph`
  - `hybrid`

## Summary Output Formats

`POST /api/v1/documents/summary` supports MarkItDown-aligned output formats:

- `md`
- `markdown`
- `txt`

Response returns a presigned-style URL (local or S3-backed depending on adapter mode).

## Endpoints

### Core

- `GET /api/v1/health`
- `GET /api/v1/ready`
- `GET /api/v1/metrics`
- `GET /api/v1/documents`
- `POST /api/v1/documents`
- `POST /api/v1/documents/generate`
- `POST /api/v1/documents/summary`
- `POST /api/v1/chat/sessions`
- `DELETE /api/v1/chat/sessions/{id}`
- `POST /api/v1/documents/chat`

Detailed contract file:

- `documentation/openapi/openapi.v1.yaml`

## Project Structure

- `src/document_analyzer_api/api/`: routes, schemas, RFC7807 error mapping.
- `src/document_analyzer_api/application/`: orchestration services.
- `src/document_analyzer_api/domain/`: models and ports.
- `src/document_analyzer_api/infrastructure/`: adapters (MarkItDown, Mongo, Neo4j, MinIO, Ollama, modalities).
- `src/document_analyzer_api/bootstrap/container.py`: dependency composition root.
- `documentation/`: refined specs, conventions, and implementation plan.
- `tests/`: unit and integration tests.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

## Run

```bash
uvicorn document_analyzer_api.main:app --host 0.0.0.0 --port 8000 --workers 1
```

```bash
python -m document_analyzer_api.main
```

## Docker Compose

```bash
docker compose up --build
```

## Real Mode

Real mode switches adapters to real dependencies (`ADAPTER_MODE=real`):

- MongoDB (metadata, chunks, chat history)
- Neo4j (graph chunks + graph retrieval)
- MinIO/S3 (raw files + outputs)
- Ollama (embeddings, generation, image)
- `../llm-tts-api` for TTS

Useful starting point:

```bash
cp .env.real.example .env.real
```

Smoke test (gated):

```bash
RUN_REAL_E2E=1 python -m pytest -m real_e2e
```

## Testing

```bash
python -m pytest -q
```

## Key Files To Read First

- `src/document_analyzer_api/bootstrap/container.py`
- `src/document_analyzer_api/api/routes/documents.py`
- `src/document_analyzer_api/application/services/document_processing_pipeline_service.py`
- `src/document_analyzer_api/infrastructure/parsing/markitdown_document_parser.py`
- `src/document_analyzer_api/infrastructure/parsing/markitdown_document_creator.py`
