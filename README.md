# Document Analyzer API

This is the implementation workspace for `document-analyzer`.

## Current Status

Implemented so far:

- FastAPI app with `/api/v1/health` and `/api/v1/ready`
- Clean architecture folder layout (domain/application/infrastructure/api)
- Typed settings via a dataclass + environment variables
- Dependency readiness adapters for MongoDB, Neo4j, MinIO, and Ollama
- Local Docker Compose stack
- RFC 7807 centralized error responses
- `GET /api/v1/documents` contract with pagination
- `POST /api/v1/documents` sync ingestion v1 behavior:
  - epub-only validation
  - per-file partial results
  - duplicate name/hash conflict handling
  - `.done` marker skip/reprocess behavior
- Chunking foundation services for Phase 4 with two strategies:
  - `meaningful`
  - `contextual_summary` (deterministic summarizer stub for now)
- Unit and integration tests

## Quick Start

1. Copy env file:

```bash
cp .env.example .env
```

2. Install dependencies:

```bash
python -m pip install -e .[dev]
```

3. Run tests:

```bash
python -m pytest
```

4. Run API locally:

```bash
uvicorn document_analyzer_api.main:app --reload --host 0.0.0.0 --port 8000
```

5. Check endpoints:

- `GET http://localhost:8000/api/v1/health`
- `GET http://localhost:8000/api/v1/ready`

## Docker Compose

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

## Real Mode Smoke

You can switch adapter composition to real providers by setting `ADAPTER_MODE=real` and the required env vars.
Recommended baseline for real mode is MongoDB `8.2+` and Neo4j `6`.
Real-mode TTS is integrated via sibling `../llm-tts-api` (compose service `tts-api`), and image generation prefers
Ollama image endpoints when available.

Start from the real env template:

```bash
cp .env.real.example .env.real
```

To run the gated real-mode smoke test:

```bash
RUN_REAL_E2E=1 python -m pytest -m real_e2e
```

Or use the helper script that starts required dependencies and runs the smoke suite:

```bash
./scripts/run_real_mode_smoke.sh
```



