# Document Analyzer - Refined Specs (V1)

## 1) Scope and Goals

V1 is an internal-only API service that:

- Ingests EPUB files only.
- Stores original files in S3-compatible storage (MinIO locally).
- Parses EPUB content and creates chunked RAG data in both MongoDB and Neo4j.
- Supports document listing, summary generation, one-shot generation, and stateful chat.
- Supports text, audio, and image outputs.
- Uses Ollama as the LLM/embedding provider for V1.

Out of scope for V1:

- Auth and multi-tenancy.
- Re-ranking and confidence score.
- Additional file formats (must return 415).

## 2) Runtime and Deployment

- Local-first deployment with Docker Compose.
- Required services: API app, MongoDB, Neo4j, Ollama, MinIO.
- Architecture must preserve clear interfaces to allow future cloud deployment with minimal code changes.
- Real-mode recommended baseline versions: MongoDB `8.2+` (vector search support) and Neo4j `6`.

Implementation policy:

- Local deterministic adapters are allowed during first implementation pass to validate contracts and orchestration.
- After all planned V1 features are completed with local adapters, a second pass is mandatory to replace local adapters with real integrations requested for V1 runtime:
  - MongoDB repositories
  - MongoDB chat session repository with TTL
  - Neo4j repositories
  - Ollama generation/embedding integration
  - MinIO/S3 storage integration
  - real audio provider integration (use sibling `epub/llm-tts-api`)
  - real image provider integration (prefer Ollama image generation when available)

## 3) API Versioning and Error Format

- Versioning: URI-based only (`/api/v1`).
- Error schema: RFC 7807 Problem Details (`application/problem+json`).
- Problem details should include at least:
  - `type`
  - `title`
  - `status`
  - `detail`
  - `instance`
  - `errorCode` (extension field)
  - `details` (extension field, optional structured validation details)

## 4) Endpoint Contracts

## 4.1 POST /api/v1/documents

Uploads one or more files and processes each file synchronously in the same request.

### Request

- Content type: `multipart/form-data`
- Fields:
  - `files`: one or more files
  - `chunking`: optional JSON object applied to all files in the request
  - Optional metadata fields per file (name aliases if needed)

`chunking` object (optional):

- `strategy`: `meaningful` (default) | `contextual_summary`
- `granularity`: `chapter` | `paragraph` (default) | `sub_paragraph_tokens`
- `subParagraph`: optional object used only when `granularity=sub_paragraph_tokens`
  - `targetTokens`
  - `overlapTokens`
- `strategyOptions`: optional object for strategy-specific fields
  - `contextualSummary.prompt`: optional prompt defining summary criteria (default: normal concise summary)

### Validation

- Only `.epub` accepted in V1; all other formats return per-file status 415.
- Upload limits controlled by environment variables:
  - `MAX_FILES_PER_REQUEST` (default unlimited)
  - `MAX_FILE_SIZE_BYTES` (default unlimited)
  - `MAX_TOTAL_PAYLOAD_BYTES` (default unlimited)

### Idempotency and Duplicate Rules

For each uploaded file name:

1. If file name does not exist in object storage: upload and process.
2. If file name exists:
   - Compare content hash.
   - If different hash: return per-file conflict (`409`).
   - If same hash:
     - If corresponding `.done` trailer exists: skip processing and return success (`already_processed`).
     - If `.done` does not exist: reprocess.
3. `.done` trailer is trusted as final processing marker. No DB consistency check is required before skipping.

### Processing Behavior

Synchronous per request, per file:

1. Upload original file to object storage.
2. Parse EPUB preserving document hierarchy.
3. Build base chunks using selected chunking granularity.
4. Apply selected chunking strategy and enrich metadata.
   - `meaningful` (default): keep chunk text as meaningful source chunk (chapter/paragraph/sub-paragraph piece).
   - `contextual_summary`: keep the same base chunks, but transform each chunk content into an LLM summary generated with broader context:
     - if granularity is `paragraph` or `sub_paragraph_tokens`, provide at least the full chapter as context and instruct model to summarize only the target chunk,
     - if granularity is `chapter`, chapter context is enough.
     - if `strategyOptions.contextualSummary.prompt` is provided, use it as summarization criteria (for example: only important happenings).
   - In `contextual_summary`, keep source text traceability in metadata (`sourceExcerpt` or equivalent field).
5. Generate embeddings.
6. Persist chunks into MongoDB and Neo4j.
7. Generate and persist document description (used in list endpoint).
8. Remove temporary TTL from chunk records only after whole-file processing succeeds.
9. Write empty `.done` trailer in object storage.

### Failure Handling

- Partial success across files is allowed (multi-status style payload).
- On parse/embedding failure for a file:
  - return immediate per-file error,
  - keep temporary chunk records with TTL for automatic cleanup.

### Response

- HTTP status:
  - `200` when all files successful,
  - `207` when mixed per-file outcomes,
  - `400` for request-level invalid multipart payload,
  - `500` for non-recoverable request-level failure.
- Body: per-file status entries including `documentId` (when available), `name`, `status`, and error info.

## 4.2 GET /api/v1/documents

Returns paginated document list.

### Query Params

- `offset` (default 0)
- `limit` (default from env)

### Response Fields

Each item includes exactly:

- `id`
- `name`
- `description`

## 4.3 POST /api/v1/documents/summary

Creates a new EPUB summary/synthesis document synchronously.

### Request JSON

- `documentIds`:
  - omitted => use all documents
  - `[]` => use none (valid)
  - `null` => `400`
- `keywords`: optional
- `keywordsMode`: `metadata_only` (default) | `filter` | `rank_boost`
- `outputFormat`: `epub`
- `generationOptions`: provider-specific options (for V1: Ollama schema)
- Retrieval overrides and mode (see Retrieval section)

### Response

- Presigned URL only.

## 4.4 POST /api/v1/documents/generate

One-off question answering over selected documents.

### Request JSON (core)

- `question` (required)
- `documentIds` rules same as above
- `keywords` optional
- `keywordsMode`: `metadata_only` (default) | `filter` | `rank_boost`
- `retrievalMode`: `vector` | `graph` | `hybrid`
- `retrievalOptions` object with common and mode-specific fields
- `outputFormat`: `text` | `audio` | `image` | `text+image`
- `includeSources`: boolean (default `false`)
- `stream`: boolean (default `true`)
- `generationOptions`: provider-scoped object

### Streaming

- Streaming format follows Ollama-style JSON lines/chunked events.
- Default is streaming (`stream=true`).
- For audio output, response is direct downloadable binary stream (wav by default).
- For image output, response returns integrated JSON payload with generated image content and answer.
- For `text+image`, response returns text answer plus integrated image payload.

## 4.5 Chat Endpoints

### POST /api/v1/chat/sessions

Creates a server-side chat session.

### DELETE /api/v1/chat/sessions/{id}

Deletes a chat session and related persisted context.

### POST /api/v1/documents/chat

Chat with server-side memory.

- Requires `sessionId` in request body.
- Supports same retrieval and output controls as `/generate`.
- Supports streaming in Ollama-style format.

### Context Compaction

- Automatic compaction when context budget is near limit.
- On-demand compaction when caller requests it (e.g., `compactContext=true`).
- Conversation history stored in MongoDB with TTL.

## 5) Data Model (Domain)

## 5.1 Document Chunk (logical)

- `id`
- `referenceDocumentId`
- `referenceChunkIndex`
- `content`
- `embedding`
- `language`
- `keywords`
- `metadata` (generic container for format-specific fields, including EPUB hierarchy)
- `connections` (for graph relations when needed)

Notes:

- Keep format-specific fields inside `metadata`.
- Language is per chunk; if missing, detect during processing.
- Chunking-specific metadata should include at least:
  - `chunkingStrategy`
  - `chunkGranularity`
  - source span information (chapter/paragraph/offset range)
  - source excerpt reference when using `contextual_summary`

## 5.2 Document Metadata (for list)

- `id`
- `name`
- `description` (LLM-generated during processing)

## 6) Retrieval and RAG Rules

Supported retrieval modes:

- `vector`
- `graph`
- `hybrid`

Keyword behavior controlled by `keywordsMode`:

- `metadata_only` (default)
- `filter`
- `rank_boost`

Strict anti-hallucination policy:

- If evidence is insufficient, answer exactly:
  - `I cannot find enough support in selected documents.`

Citations:

- Optional (`includeSources=false` by default).
- Granularity: chunk-level.

## 7) Defaults (V1)

## 7.1 Generation Defaults

- Provider: `ollama`
- Model: `qwen3.5:9b`
- `temperature`: `0.2`
- `top_p`: `0.9`
- `max_tokens`: `-1` (provider unlimited mode)

## 7.2 Retrieval Defaults

- `topK`: `8`
- `minScore`: `0.2`
- `retrievalMode`: `vector`
- `includeSources`: `false`
- `hybridAlpha`: `0.5` (when hybrid mode is selected)

## 7.3 Output Defaults

- `stream`: `true`
- Audio format default: `wav`
- TTS model default: `Qwen/Qwen3-TTS-12Hz-0.6B-Base`

## 7.4 TTL Defaults

- Temporary chunk TTL: `10m`
- Chat history TTL: `7d`

Both configurable via environment variables.

## 7.5 Chunking Defaults

- `strategy`: `meaningful`
- `granularity`: `paragraph`
- `subParagraph.targetTokens`: `350`
- `subParagraph.overlapTokens`: `60`
- `strategyOptions.contextualSummary.prompt`: `Write a concise neutral summary of the target chunk.`

## 8) Storage Strategy

- Object storage (MinIO/S3-compatible) is source of truth for uploaded document objects.
- MongoDB and Neo4j store processed chunk data for retrieval.
- Both MongoDB and Neo4j must contain ingested chunk data in V1.

## 9) Observability

- Structured logging (JSON logs).
- Metrics via Prometheus.
- Tracing via OpenTelemetry.
- Expose metrics endpoint at `GET /api/v1/metrics` in Prometheus text format.
- Keep observability adapter interfaces clean for future backend swaps.

Provider hardening:

- Provider-facing calls must use timeout and retry policies (configurable via environment variables).
- Retry behavior should include bounded attempts and backoff.

## 10) Testing and Quality Gates

- Unit tests are mandatory with line coverage >= 80%.
- Integration tests required where meaningful (ingestion path, retrieval modes, chat/session flow, modality output paths).
- Include contract tests for RFC 7807 errors and streaming behavior.

## 11) Extensibility Requirements

Design with interfaces/ports so future changes are low-risk:

- New file parsers and creators.
- Additional embedding/generation/TTS/image providers.
- Additional retrieval backends.
- Async execution path for summary/generation if enabled later.

## 12) Environment Variables (minimum)

- `MAX_FILES_PER_REQUEST`
- `MAX_FILE_SIZE_BYTES`
- `MAX_TOTAL_PAYLOAD_BYTES`
- `TEMP_CHUNK_TTL_SECONDS`
- `CHAT_HISTORY_TTL_SECONDS`
- `DEFAULT_TOP_K`
- `DEFAULT_MIN_SCORE`
- `DEFAULT_HYBRID_ALPHA`
- `DEFAULT_GENERATION_MODEL`
- `DEFAULT_TTS_MODEL`
- `DEFAULT_TTS_VOICE`
- `DEFAULT_AUDIO_FORMAT`
- `DEFAULT_CHUNKING_STRATEGY`
- `DEFAULT_CHUNK_GRANULARITY`
- `DEFAULT_SUBPARAGRAPH_TARGET_TOKENS`
- `DEFAULT_SUBPARAGRAPH_OVERLAP_TOKENS`
- `PROVIDER_RETRY_COUNT`
- `PROVIDER_TIMEOUT_SECONDS`
- `PROVIDER_BACKOFF_SECONDS`
- `ADAPTER_MODE` (`local` or `real`)
- `MONGODB_URI`
- `MONGODB_DATABASE`
- `MONGODB_VECTOR_INDEX_NAME`
- `NEO4J_URI`
- `NEO4J_USER`
- `NEO4J_PASSWORD`
- `S3_ENDPOINT`
- `S3_ACCESS_KEY`
- `S3_SECRET_KEY`
- `S3_BUCKET_RAW`
- `S3_BUCKET_OUTPUT`
- `OLLAMA_BASE_URL`
- `OLLAMA_EMBEDDING_MODEL`
- `OLLAMA_TEXT_MODEL`
- `TTS_API_BASE_URL`
- `IMAGE_API_BASE_URL`
- `IMAGE_MODEL`
- `OLLAMA_IMAGE_MODEL`







