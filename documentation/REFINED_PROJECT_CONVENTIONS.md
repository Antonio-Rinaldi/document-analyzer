# Refined Project Conventions

## 1) Language and Style

- Use Python.
- Follow conventions already used in sibling projects under `../epub`.
- Use clear, meaningful names.
- Prefer concise Pythonic constructs when they improve readability.
- Keep functions small and focused.
- Use ASCII by default in source files.

## 2) Typing and Validation

- Add type hints for all functions/methods, including return types.
- Use Pydantic models for API requests/responses and internal validated DTOs.
- Validate boundary inputs at adapter level (HTTP, storage, providers).
- Use strict validation for enums and nullable semantics (for example `documentIds=null` => 400).

## 3) Architecture

Use clean architecture with explicit ports and adapters.

Core services:

- `DocumentService`
- `ChatService`
- `AudioService`
- `ImageService`

Ports (interfaces):

- `DocumentRepository` (Mongo + Neo4j adapters)
- `DocumentStorage` (S3/MinIO adapter)
- `DocumentParser` (MarkItDown-backed parser)
- `DocumentCreator` (summary document creator)
- `AIEmbeddingClient`
- `AITextClient`
- `AITTSClient`
- `AIImageClient`
- `RetrievalBackend` (vector, graph, hybrid strategy adapters)

Rules:

- Business logic must not import infrastructure libraries directly.
- Provider-specific option schemas belong to provider adapters, not global generic models.
- Keep mode-specific retrieval options in dedicated sub-objects.

## 4) Data and Model Conventions

- Keep format-specific fields inside generic `metadata` fields.
- Preserve EPUB hierarchy metadata in chunks.
- Language metadata is per chunk.
- Ensure Mongo and Neo4j ingestion consistency per successful document processing.
- For Neo4j variable-length relationship traversal (`*min..max`), render hop bounds as validated literal integers in the
  Cypher string; do not pass hop depth as a Cypher query parameter.

## 5) API Conventions

- API base path uses URI versioning (`/api/v1`).
- Use RFC 7807 for errors (`application/problem+json`).
- For multi-file ingestion, return per-file status in one response.
- Streaming format for chat/generate follows Ollama-style chunked JSON semantics.
- Keep format validation capability-driven and expose it via `GET /api/v1/documents/capabilities`.

## 6) Error Handling

- Never swallow exceptions silently.
- Convert known domain/infrastructure failures into typed domain errors.
- Map errors centrally to RFC 7807 responses.
- Include stable `errorCode` values for client handling.

## 7) Logging, Metrics, Tracing

- Use logging, never `print`.
- Structured logs with consistent fields (`request_id`, `session_id`, `document_id`, `operation`, `duration_ms`).
- Expose Prometheus metrics.
- Instrument OpenTelemetry traces for key flows:
  - document ingestion
  - parse/chunk/embed/persist
  - retrieval
  - generation/chat
- Keep tracing isolated from business logic classes: use decorator/wrapper components around services instead of
  calling tracing primitives directly inside use-case methods.
- In local docker-compose profile, expose Jaeger for trace visualization and troubleshooting.

## 8) Configuration

- All operational limits and defaults must be environment-configurable.
- Keep sensible defaults for local development.
- Centralize config in one module using typed settings.
- Fail fast at startup on invalid critical config.

## 9) Testing

- Unit test coverage must be >= 80%.
- Add integration tests where needed for:
  - API contracts and validation
  - ingestion end-to-end over MinIO + Mongo + Neo4j
  - retrieval modes (`vector`, `graph`, `hybrid`)
  - chat session lifecycle and TTL behavior
  - streaming behavior
- Prefer deterministic tests with stubs/mocks for LLM provider calls.

## 10) Dependency Injection and Composition

- Use dependency injection to wire services to ports.
- Keep composition root isolated (application bootstrap).
- Avoid globals and hidden shared mutable state.

## 11) Documentation and ADRs

- Write docstrings for non-trivial public functions/methods.
- Keep Markdown docs in `document-analyzer/` updated when contracts change.
- Record major architectural choices as ADR entries (short markdown files), especially:
  - sync ingestion strategy
  - dual-store persistence (Mongo + Neo4j)
  - retrieval mode design
  - streaming protocol choice

## 12) Backward-Compatible Evolution

- Design interfaces to allow:
  - new providers
  - async processing migration
  - additional modalities
  - additional document formats
- Prefer additive request fields and non-breaking response changes in V1.x.

