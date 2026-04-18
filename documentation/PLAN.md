# Implementation Plan (V1)

## 0) Goal

Deliver a production-grade internal Document Analyzer V1 with:

- MarkItDown-supported ingestion formats.
- Dual persistence for RAG chunks (MongoDB + Neo4j).
- Retrieval modes (`vector`, `graph`, `hybrid`).
- Summary, generate, and chat endpoints.
- Text, audio, image outputs.
- Observability and quality gates.

## 1) Milestones

- [x] M1: Project skeleton and local platform.
- [x] M2: API contracts and validation layer.
- [x] M3: Synchronous ingestion with idempotency and `.done` logic.
- [x] M4: Chunking, embeddings, dual-store persistence.
- [x] M5: Retrieval engines (vector, graph, hybrid).
- [x] M6: Generate and summary flows.
- [x] M7: Chat sessions, TTL, and context compaction.
- [x] M8: Modalities (audio/image) and streaming behavior.
- [x] M9: Observability, tests, and hardening.
- [x] M10: Replace local adapters with requested real integrations.
- [x] M11: MarkItDown format integration for ingestion and summary output.
- [x] M12: Runtime capability discoverability and spec alignment.
- [x] M13: Detailed OpenAPI contract documentation.
- [x] M14: Project-wide module pydoc + tracing isolation via decorators.
- [x] M15: Detailed symbol-level pydoc refinement + Jaeger local tracing stack.
- [x] M16: Narrative, method-specific technical docstrings (non-template style).
- [x] M17: Full-project manual-quality narrative docstring pass.
- [x] M18: Narrative docstring pass stabilization (non-template, self-safe tooling).
- [x] M19: IntelliJ HTTP endpoint collection and README linkage.
- [x] M20: Hierarchical Neo4j knowledge graph v1 (Document->Chapter->Paragraph->Chunk) + graph traversal depth controls.
- [x] M21: Neo4j graph phase 2 hardening (hierarchy-only reads/writes + NEXT sequencing + path-depth ranking).
- [x] M22: Image modality resilience hardening (provider 404/failure degradation without endpoint 500).
- [x] M23: Summary endpoint RAG+LLM orchestration (retrieval-driven evidence synthesis).

## 2) Phase-by-Phase Plan

## Progress Update (2026-04-11)

- Phase 1 completed.
- Phase 2 completed.
- Phase 3 completed.
- Phase 4 completed: parser -> chunking -> strategy -> embedding -> dual persistence pipeline is wired in synchronous
  ingestion, with staged TTL then commit semantics and document description persistence.
- Phase 5 completed: retrieval service and strategy backends (`vector`, `graph`, `hybrid`) implemented with
  `keywordsMode` handling and chunk-level citation support.
- Phase 6 completed: `POST /api/v1/documents/generate` and `POST /api/v1/documents/summary` implemented (sync),
  including strict insufficient-evidence handling and Ollama-style streaming behavior for generate.
- Phase 7 completed: chat session lifecycle (`POST/DELETE /api/v1/chat/sessions`) and `POST /api/v1/documents/chat`
  implemented with server-side history, TTL-backed persistence, automatic and on-demand context compaction.
- Phase 8 completed: modality support wired for text/audio/image/text+image with direct audio binary response and
  integrated image payload behavior for generate/chat.
- Phase 9 completed: structured request logging middleware, Prometheus-style `/api/v1/metrics` endpoint, tracing hooks
  in core services, and provider retry/timeout wrappers were added and validated by tests.
- Phase 10 completed: runtime now uses a single real-integrations path wired for S3 storage,
  MongoDB metadata/chunks, Neo4j chunks, Ollama embedding/summarization, Ollama text generation + real retrieval
  backends, MongoDB chat sessions (TTL), and HTTP-based audio/image providers. Gated `real_e2e` coverage includes
  startup smoke plus full ingest/list/generate/summary/chat/session lifecycle flow scaffolding. Runtime execution
  tooling is in place (`.env.example`/`.env` runtime setup and `scripts/run_real_mode_smoke.sh`).
  MongoDB real retrieval now uses `$vectorSearch` (with lexical fallback when index is unavailable) and runtime
  configuration includes `MONGODB_VECTOR_INDEX_NAME`; compose dependencies were aligned to MongoDB 8.2 and Neo4j 6.
  Real-mode TTS now targets sibling `epub/llm-tts-api`, and image generation prefers Ollama with fallback provider.
  Remaining work: execute and validate these flows against running dependencies and finalize production
  hardening defaults.
- Phase 11 completed (2026-04-14): document parsing now uses Microsoft MarkItDown in ingestion, input validation is
  extension-driven from MarkItDown capabilities, and summary output now supports MarkItDown-aligned output formats
  (`md`, `markdown`, `txt`).
- Phase 12 completed (2026-04-14): `GET /api/v1/documents/capabilities` now exposes supported input extensions and
  summary output formats; refined specs and project conventions were aligned with implemented MarkItDown behavior.
- Phase 13 completed (2026-04-14): detailed OpenAPI specification added at
  `documentation/openapi/openapi.v1.yaml`, covering all exposed endpoints, request/response payloads, modality-specific
  behaviors (NDJSON stream, JSON payloads, audio binary), and RFC 7807 error contracts.
- Phase 14 completed (2026-04-14): tracing calls were removed from business logic and moved to decorator/wrapper
  instrumentation components, and module-level pydoc documentation was added across all Python files in `src/` and
  `tests/`.
- Phase 15 completed (2026-04-14): module/class/function docstrings were refined with more specific detailed content,
  tracing runtime configuration gained OTLP export options, and Docker Compose now includes Jaeger all-in-one for
  local trace visualization.
- Phase 16 completed (2026-04-14): docstring generation was upgraded from template-like text to narrative,
  method-specific technical descriptions with module purpose mapping, parameter semantics, behavior summaries, and
  return-contract hints derived from function annotations and AST call patterns.
- Phase 17 completed (2026-04-14): a full-project pass was executed across all Python files to enforce narrative,
  technical, non-template documentation at module/class/function level with syntax validation and full test-suite
  confirmation.
- Phase 18 completed (2026-04-14): docstring pass tooling was stabilized to avoid self-rewrite regressions and to keep
  narrative, non-template wording consistent across repeated full-repository runs.
- Phase 19 completed (2026-04-14): created `document-analyzer.http` with endpoint-by-endpoint IntelliJ requests
  (health, readiness, metrics, ingest, list, capabilities, summary, generate variants, chat lifecycle) and linked it
  from `README.md`.
- Operational continuation (2026-04-14): added targeted observability instrumentation tests in
  `tests/unit/test_observability_instrumentation.py` (metered async/sync + traced sync attribute-builder fallback),
  switched real-profile `tts-api` compose service to Docker build mode using sibling `../llm-tts-api/Dockerfile`,
  and aligned container defaults to `TTS_VOICE_MAP_FILE=/app/config/voice_map.container.json`.
- Validation snapshot (2026-04-14): targeted suites passed for
  `tests/unit/test_observability_instrumentation.py`, `tests/integration/test_health_endpoints.py`,
  `tests/unit/test_settings.py`, plus `../llm-tts-api/tests/test_config.py`,
  `../llm-tts-api/tests/test_startup_preload.py`, and `../llm-tts-api/tests/test_audio_speech.py`.
- Operational continuation (2026-04-15): removed runtime legacy branches and mode toggles from configuration and
  composition paths. `document-analyzer` now runs a single real-integrations implementation (MongoDB, Neo4j, MinIO,
  Ollama, HTTP TTS/image providers), and legacy embedding endpoint fallbacks were removed in favor of the modern
  `/api/embeddings` flow used by runtime ingestion.
- Operational continuation (2026-04-15): S3 summary output now returns a real presigned download URL instead of an
  internal `s3://` locator; runtime configuration now includes `S3_OUTPUT_PRESIGN_TTL_SECONDS`, with startup
  validation and focused unit coverage for presigned URL generation.
- Operational continuation (2026-04-17): per-file ingestion failures now emit error logs with full stack traces in
  `DocumentIngestionService.ingest_files` before returning structured API failure entries, improving production
  diagnostics for errors like `INGESTION_FAILED` without changing response contracts.
- Operational continuation (2026-04-17): ingestion pipeline now enforces strict chunk-to-embedding cardinality before
  persistence to prevent index-based crashes when provider payloads are malformed. `OllamaEmbeddingClient` validates
  `/api/embeddings` response shape/count, and regression coverage was added for cardinality mismatch and invalid
  payload behavior.
- Operational continuation (2026-04-17): endpoint integration tests were stabilized to run deterministically with
  local/deterministic adapters via an in-test container override in `tests/integration/test_documents_endpoints.py`,
  avoiding external Ollama/TTS/image endpoint dependencies while preserving API contract assertions.
- Validation snapshot (2026-04-17): passed `tests/integration/test_documents_endpoints.py`,
  `tests/integration/test_health_endpoints.py`, `tests/unit/test_ollama_embedding_client.py`,
  `tests/unit/test_document_processing_pipeline_service.py`, `tests/unit/test_settings.py`, and full
  `python3 -m pytest -q tests -m 'not real_e2e'`.
- Operational continuation (2026-04-17): hardened real ingestion embedding execution by introducing
  `OLLAMA_EMBEDDING_BATCH_SIZE` and batched `/api/embeddings` requests in `OllamaEmbeddingClient`, preventing very
  large single-request payloads from returning malformed provider responses during large-book ingestion.
- Operational continuation (2026-04-17): embedding payload normalization now also accepts OpenAI-compatible
  `data[].embedding` responses while preserving strict one-vector-per-input cardinality checks.
- Operational continuation (2026-04-17): added safe diagnostic logging in `OllamaEmbeddingClient` for
  `/api/embeddings` HTTP failures, non-JSON responses, cardinality mismatches, and invalid payload shapes, including
  payload structure hints (keys/types/lengths) and expected batch count without logging raw chunk text.
- Operational continuation (2026-04-17): `OllamaEmbeddingClient` now detects single-embedding payload shape
  (`{"embedding": ...}`) returned for batched input and automatically falls back to scalar per-text embedding calls,
  with explicit fallback logs and unit regression coverage.
- Operational continuation (2026-04-17): removed scalar fallback and aligned runtime embedding calls to Ollama
  `/api/embed` batched semantics as the direct integration path. Empty/single-vector `embedding` payloads now fail fast
  with diagnostics so model/endpoint mismatches are explicit instead of silently retried.
- Operational continuation (2026-04-17): increased provider execution timeout defaults for real ingestion
  (`PROVIDER_TIMEOUT_SECONDS=60.0`) and documented timeout tuning in env templates/README to prevent premature
  `asyncio.wait_for` cancellation during embedding-heavy book ingestion.
- Operational continuation (2026-04-17): retry wrapper timeout failures now surface descriptive timeout messages
  (attempt index + timeout budget), and ingestion error mapping guarantees a non-empty per-file `error` field even when
  providers raise exceptions with blank string payloads (for example bare `TimeoutError`).
- Operational continuation (2026-04-18): Neo4j chunk persistence now writes a hierarchy graph
  (`Document -> Chapter -> Paragraph -> Chunk`) with stable chapter/paragraph metadata keys produced during chunk
  building, while preserving a compatibility `Document -> Chunk` edge for read fallback. Graph retrieval now applies
  bounded hop traversal (`graph.maxHops`, default `2`) and injects path/connectivity metadata for graph ranking.
- Operational continuation (2026-04-18): removed Neo4j legacy `Document -> Chunk` compatibility edges and fallback
  reads. Persistence now maintains hierarchy-only topology plus deterministic `NEXT` ordering edges for chapters,
  paragraphs, and paragraph-local chunks. Graph retrieval traversal now expands across containment + `NEXT` edges and
  emits `connections`, `graphPathCount`, and `graphMinDepth` metadata for graph-aware ranking heuristics.
- Operational continuation (2026-04-18): image providers were hardened to avoid uncaught `httpx` exceptions in
  `/documents/generate` and `/documents/chat` image flows. Upstream 404/HTTP failures now return structured
  `image/unsupported` payloads with warnings, preserving answer delivery and preventing modality-path runtime 500s.
- Operational continuation (2026-04-18): `/documents/summary` now uses retrieval-driven evidence assembly and
  text-generation synthesis instead of metadata-description concatenation. API schema/routes now pass
  `keywordsMode`/`retrievalMode`/`retrievalOptions` through to summary orchestration, and integration/unit coverage
  validates generated summary content is RAG-backed.
- Validation snapshot (2026-04-18): passed `tests/unit/test_document_summary_service.py`,
  `tests/integration/test_documents_endpoints.py`, and `tests/unit/test_observability_instrumentation.py` after
  summary RAG orchestration rollout, including retrieval-controls coverage for `/documents/summary`.
- Operational continuation (2026-04-18): fixed Neo4j graph retrieval Cypher generation to render
  `graph.maxHops` as a validated literal in variable-length path traversal (`*1..N`) instead of a query parameter,
  resolving runtime `CypherSyntaxError` failures in `/documents/summary` graph/hybrid retrieval paths; added unit
  regression coverage for hop normalization, literal query generation, and no-parameter `session.run` execution.
- Operational continuation (2026-04-18): `/documents/summary` now accepts optional `summaryWordCount` and threads it
  through route/service/observability layers as prompt-level length guidance (`approximately N words`) while preserving
  additive backward compatibility and strict insufficient-evidence fallback behavior.
- Operational continuation (2026-04-18): removed the `/documents/summary.summaryWordCount` upper validation cap so
  large positive targets are accepted while preserving lower-bound validation (`>= 1`) and backward-compatible prompt
  guidance behavior.

## Phase 1 - Foundation

Scope:

- Create service structure (domain/application/infrastructure/api).
- Define ports/interfaces.
- Add typed settings and env handling.
- Add Docker Compose with MongoDB, Neo4j, MinIO, Ollama, API.

Acceptance:

- App boots locally.
- Health endpoint works.
- Services connect to dependencies.

## Phase 2 - API Contracts

Scope:

- Implement `/api/v1` routing.
- Define Pydantic request/response models.
- Implement RFC 7807 error mapper.
- Implement pagination schema for documents list.

Acceptance:

- Validation rules enforced, including `documentIds` semantics.
- Problem Details responses are stable and tested.

## Phase 3 - Ingestion Pipeline (Sync)

Scope:

- Implement `POST /api/v1/documents` multipart handling.
- Enforce MarkItDown-supported input validation and upload limits.
- Implement duplicate name/hash checks.
- Implement `.done` skip/reprocess logic.
- Support partial success per file.

Acceptance:

- Same-name+same-hash behavior matches spec.
- Same-name+different-hash returns per-file 409.
- `.done` short-circuit tested.

## Phase 4 - Parse, Chunk, Embed, Persist

Scope:

- Implement EPUB parser preserving hierarchy.
- Implement chunking strategy interface with request-selectable strategy and granularity.
- Implement `meaningful` chunking strategy (default).
- Implement `contextual_summary` chunking strategy (LLM summarizes each base chunk with chapter-level context when
  needed).
- Support optional custom summarization criteria prompt for `contextual_summary` strategy.
- Implement granularity options: `chapter`, `paragraph`, `sub_paragraph_tokens`.
- Add per-chunk language detection fallback.
- Generate embeddings via Ollama.
- Write chunks to MongoDB and Neo4j.
- Temporary TTL write + TTL removal on full success.
- Generate document description chunk.

Acceptance:

- Successful files persist complete data in both stores.
- Failures keep temp TTL data and return errors.
- Chunk strategy/granularity request params are validated and honored.

## Phase 5 - Retrieval Engine

Scope:

- Implement retrieval strategy interface.
- Implement `vector` strategy.
- Implement `graph` strategy.
- Implement `hybrid` strategy with `hybridAlpha`.
- Implement `keywordsMode` behavior.

Acceptance:

- Retrieval mode and options respected per request.
- Citations available at chunk granularity when requested.

## Phase 6 - Generation + Summary

Scope:

- Implement `POST /api/v1/documents/generate`.
- Implement `POST /api/v1/documents/summary` (sync).
- Add strict insufficient-evidence behavior.
- Implement streaming format aligned with Ollama style.

Acceptance:

- Generate supports stream default true.
- Summary returns presigned URL only and validates output formats (`md`, `markdown`, `txt`).

## Phase 7 - Chat Sessions

Scope:

- Implement `POST /api/v1/chat/sessions`.
- Implement `DELETE /api/v1/chat/sessions/{id}`.
- Implement `POST /api/v1/documents/chat` with `sessionId`.
- Persist chat history in Mongo with TTL.
- Add automatic and on-demand context compaction.

Acceptance:

- Session lifecycle works end-to-end.
- Compaction behavior is test-covered.

## Phase 8 - Modalities

Scope:

- Text output.
- Audio output with direct downloadable binary stream.
- Default audio format `wav` and default model `Qwen/Qwen3-TTS-12Hz-0.6B-Base`.
- Image output integrated with answer.

Acceptance:

- `outputFormat` controls modality behavior correctly.
- All required modalities are available.

## Phase 9 - Observability and Hardening

Scope:

- Add structured logs.
- Expose Prometheus metrics.
- Add OpenTelemetry tracing.
- Improve retry/timeout/circuit behavior for provider calls.
- Final docs and operational runbook.

Acceptance:

- Key flows are traceable.
- Metrics dashboards can be built from exported metrics.

## Phase 10 - Production Integrations (Post-Local)

Scope:

- Replace local/deterministic adapters with real adapters requested in specs.
- Implement MongoDB repositories for document metadata and chunk persistence.
- Implement Neo4j repositories for graph chunk persistence and retrieval.
- Implement Ollama-backed embedding and text generation clients.
- Implement MinIO/S3-backed document and output storage.
- Replace local placeholder audio/image providers with real providers matching requested models and formats.

Acceptance:

- V1 endpoints run end-to-end with real MongoDB, Neo4j, Ollama, and MinIO integrations.
- Runtime composition uses real integrations only.
- Contract behavior remains backward-compatible with the previously validated local pass.

## 3) Testing Strategy

- Unit tests for domain/application/infrastructure logic.
- Unit line coverage >= 80%.
- Integration tests where needed for:
    - ingestion with MinIO + Mongo + Neo4j
    - retrieval modes
    - summary/generate/chat endpoints
    - session TTL and compaction
    - streaming contracts

## 4) Implementation Order Within Team

1. Foundation + contracts first.
2. Ingestion and dual persistence.
3. Retrieval modes.
4. Generation and chat.
5. Modalities and observability.
6. Hardening and documentation.

## 5) Risks and Mitigations

- Dual-store consistency risk:
    - Mitigation: transactional-like process semantics, temp TTL writes, idempotent retries.
- Provider instability or model latency:
    - Mitigation: timeout budgets, retries, fallback error mapping.
- Streaming edge cases:
    - Mitigation: contract tests with chunk boundaries and cancellation handling.
- Graph retrieval complexity:
    - Mitigation: start with constrained traversal and clear defaults.

## 6) Definition of Done

- All endpoints implemented per refined specs.
- Unit coverage >= 80%.
- Required integration tests passing.
- Docker Compose local stack works.
- `REFINED_SPECS.md`, `REFINED_PROJECT_CONVENTIONS.md`, and `RETRIEVAL.md` are aligned with implementation.














