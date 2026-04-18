"""Tracing/metrics wrappers for domain port adapters.

These wrappers instrument adapter boundary calls so traces and metrics include
nested spans from operation -> service -> adapter execution.
"""

from __future__ import annotations

from ..domain.models.chat import ChatSession
from ..domain.models.chunking import ParsedDocument
from ..domain.models.persistence import DocumentMetadata, PersistedChunk
from ..domain.models.retrieval import RetrievalHit, RetrievalRequest
from ..domain.ports.chat_session_repository import ChatSessionRepositoryPort
from ..domain.ports.chunk_repository import ChunkRepositoryPort
from ..domain.ports.document_creator import CreatedDocument, DocumentCreatorPort
from ..domain.ports.document_metadata_repository import DocumentMetadataRepositoryPort
from ..domain.ports.document_parser import DocumentParserPort
from ..domain.ports.document_storage import DocumentStoragePort
from ..domain.ports.embedding_client import EmbeddingClientPort
from ..domain.ports.image_provider import ImageProviderPort
from ..domain.ports.output_storage import OutputStoragePort
from ..domain.ports.retrieval_backend import RetrievalBackendPort
from ..domain.ports.text_generation_client import TextGenerationClientPort
from ..domain.ports.text_summarizer import TextSummarizerPort
from ..domain.ports.tts_provider import TTSProviderPort
from .metrics import metered_async, metered_sync
from .tracing import traced_async, traced_sync


class TracedDocumentStorage(DocumentStoragePort):
    def __init__(self, inner: DocumentStoragePort) -> None:
        self._inner = inner

    @metered_async("adapter.document_storage", "object_exists")
    @traced_async("adapter.document_storage.object_exists", attribute_builder=lambda self, name: {"document.name": name})
    async def object_exists(self, name: str) -> bool:
        return await self._inner.object_exists(name)

    @metered_async("adapter.document_storage", "object_hash")
    @traced_async("adapter.document_storage.object_hash", attribute_builder=lambda self, name: {"document.name": name})
    async def object_hash(self, name: str) -> str:
        return await self._inner.object_hash(name)

    @metered_async("adapter.document_storage", "put_object")
    @traced_async(
        "adapter.document_storage.put_object",
        attribute_builder=lambda self, name, content: {"document.name": name, "content.bytes": len(content)},
    )
    async def put_object(self, name: str, content: bytes) -> None:
        await self._inner.put_object(name, content)

    @metered_async("adapter.document_storage", "has_done_marker")
    @traced_async("adapter.document_storage.has_done_marker", attribute_builder=lambda self, name: {"document.name": name})
    async def has_done_marker(self, name: str) -> bool:
        return await self._inner.has_done_marker(name)

    @metered_async("adapter.document_storage", "write_done_marker")
    @traced_async("adapter.document_storage.write_done_marker", attribute_builder=lambda self, name: {"document.name": name})
    async def write_done_marker(self, name: str) -> None:
        await self._inner.write_done_marker(name)


class TracedDocumentParser(DocumentParserPort):
    def __init__(self, inner: DocumentParserPort) -> None:
        self._inner = inner

    def supported_extensions(self) -> tuple[str, ...]:
        return self._inner.supported_extensions()

    @metered_async("adapter.document_parser", "parse")
    @traced_async(
        "adapter.document_parser.parse",
        attribute_builder=lambda self, document_name, content: {
            "document.name": document_name,
            "content.bytes": len(content),
        },
    )
    async def parse(self, document_name: str, content: bytes) -> ParsedDocument:
        return await self._inner.parse(document_name=document_name, content=content)


class TracedChunkRepository(ChunkRepositoryPort):
    def __init__(self, inner: ChunkRepositoryPort, backend_name: str) -> None:
        self._inner = inner
        self._backend_name = backend_name

    @metered_async("adapter.chunk_repository", "stage_chunks")
    @traced_async(
        "adapter.chunk_repository.stage_chunks",
        attribute_builder=lambda self, document_id, chunks, ttl_seconds: {
            "backend": self._backend_name,
            "document.id": document_id,
            "chunks.count": len(chunks),
            "ttl.seconds": ttl_seconds,
        },
    )
    async def stage_chunks(self, document_id: str, chunks: list[PersistedChunk], ttl_seconds: int) -> None:
        await self._inner.stage_chunks(document_id, chunks, ttl_seconds)

    @metered_async("adapter.chunk_repository", "commit_document")
    @traced_async(
        "adapter.chunk_repository.commit_document",
        attribute_builder=lambda self, document_id: {"backend": self._backend_name, "document.id": document_id},
    )
    async def commit_document(self, document_id: str) -> None:
        await self._inner.commit_document(document_id)

    @metered_async("adapter.chunk_repository", "rollback_document")
    @traced_async(
        "adapter.chunk_repository.rollback_document",
        attribute_builder=lambda self, document_id: {"backend": self._backend_name, "document.id": document_id},
    )
    async def rollback_document(self, document_id: str) -> None:
        await self._inner.rollback_document(document_id)


class TracedDocumentMetadataRepository(DocumentMetadataRepositoryPort):
    def __init__(self, inner: DocumentMetadataRepositoryPort) -> None:
        self._inner = inner

    @metered_async("adapter.document_metadata_repository", "upsert")
    @traced_async(
        "adapter.document_metadata_repository.upsert",
        attribute_builder=lambda self, document: {"document.id": document.id, "document.name": document.name},
    )
    async def upsert(self, document: DocumentMetadata) -> None:
        await self._inner.upsert(document)

    @metered_async("adapter.document_metadata_repository", "list_paginated")
    @traced_async(
        "adapter.document_metadata_repository.list_paginated",
        attribute_builder=lambda self, offset, limit: {"pagination.offset": offset, "pagination.limit": limit},
    )
    async def list_paginated(self, offset: int, limit: int) -> tuple[list[DocumentMetadata], int]:
        return await self._inner.list_paginated(offset, limit)


class TracedRetrievalBackend(RetrievalBackendPort):
    def __init__(self, inner: RetrievalBackendPort, backend_name: str) -> None:
        self._inner = inner
        self._backend_name = backend_name

    @metered_async("adapter.retrieval_backend", "retrieve")
    @traced_async(
        "adapter.retrieval_backend.retrieve",
        attribute_builder=lambda self, request: {
            "backend": self._backend_name,
            "retrieval.mode": request.retrieval_mode.value,
            "retrieval.top_k": request.top_k,
        },
    )
    async def retrieve(self, request: RetrievalRequest) -> list[RetrievalHit]:
        return await self._inner.retrieve(request)


class TracedEmbeddingClient(EmbeddingClientPort):
    def __init__(self, inner: EmbeddingClientPort) -> None:
        self._inner = inner

    @metered_async("adapter.embedding_client", "embed_texts")
    @traced_async(
        "adapter.embedding_client.embed_texts",
        attribute_builder=lambda self, texts: {"texts.count": len(texts)},
    )
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return await self._inner.embed_texts(texts)


class TracedTextGenerationClient(TextGenerationClientPort):
    def __init__(self, inner: TextGenerationClientPort) -> None:
        self._inner = inner

    @metered_async("adapter.text_generation_client", "generate_answer")
    @traced_async(
        "adapter.text_generation_client.generate_answer",
        attribute_builder=lambda self, question, context_chunks: {
            "question.length": len(question),
            "context.count": len(context_chunks),
        },
    )
    async def generate_answer(self, question: str, context_chunks: list[str]) -> str:
        return await self._inner.generate_answer(question, context_chunks)


class TracedTextSummarizer(TextSummarizerPort):
    def __init__(self, inner: TextSummarizerPort) -> None:
        self._inner = inner

    @metered_async("adapter.text_summarizer", "summarize")
    @traced_async(
        "adapter.text_summarizer.summarize",
        attribute_builder=lambda self, target_text, context_text, prompt: {
            "target.length": len(target_text),
            "context.length": len(context_text),
            "prompt.length": len(prompt),
        },
    )
    async def summarize(self, target_text: str, context_text: str, prompt: str) -> str:
        return await self._inner.summarize(target_text, context_text, prompt)


class TracedChatSessionRepository(ChatSessionRepositoryPort):
    def __init__(self, inner: ChatSessionRepositoryPort) -> None:
        self._inner = inner

    @metered_async("adapter.chat_session_repository", "create")
    @traced_async(
        "adapter.chat_session_repository.create",
        attribute_builder=lambda self, session_id, ttl_seconds: {"session.id": session_id, "ttl.seconds": ttl_seconds},
    )
    async def create(self, session_id: str, ttl_seconds: int) -> ChatSession:
        return await self._inner.create(session_id, ttl_seconds)

    @metered_async("adapter.chat_session_repository", "get")
    @traced_async("adapter.chat_session_repository.get", attribute_builder=lambda self, session_id: {"session.id": session_id})
    async def get(self, session_id: str) -> ChatSession | None:
        return await self._inner.get(session_id)

    @metered_async("adapter.chat_session_repository", "upsert")
    @traced_async(
        "adapter.chat_session_repository.upsert",
        attribute_builder=lambda self, session, ttl_seconds: {
            "session.id": session.session_id,
            "session.messages": len(session.messages),
            "ttl.seconds": ttl_seconds,
        },
    )
    async def upsert(self, session: ChatSession, ttl_seconds: int) -> None:
        await self._inner.upsert(session, ttl_seconds)

    @metered_async("adapter.chat_session_repository", "delete")
    @traced_async(
        "adapter.chat_session_repository.delete",
        attribute_builder=lambda self, session_id: {"session.id": session_id},
    )
    async def delete(self, session_id: str) -> bool:
        return await self._inner.delete(session_id)


class TracedOutputStorage(OutputStoragePort):
    def __init__(self, inner: OutputStoragePort) -> None:
        self._inner = inner

    @metered_async("adapter.output_storage", "write_output")
    @traced_async(
        "adapter.output_storage.write_output",
        attribute_builder=lambda self, filename, content, content_type=None: {
            "output.filename": filename,
            "output.bytes": len(content),
            "output.content_type": content_type or "unknown",
        },
    )
    async def write_output(self, filename: str, content: bytes, content_type: str | None = None) -> str:
        return await self._inner.write_output(filename, content, content_type)


class TracedDocumentCreator(DocumentCreatorPort):
    def __init__(self, inner: DocumentCreatorPort) -> None:
        self._inner = inner

    def supported_output_formats(self) -> tuple[str, ...]:
        return self._inner.supported_output_formats()

    @metered_async("adapter.document_creator", "create")
    @traced_async(
        "adapter.document_creator.create",
        attribute_builder=lambda self, summary_text, output_format, filename_stem: {
            "summary.length": len(summary_text),
            "output.format": output_format,
            "filename.stem": filename_stem,
        },
    )
    async def create(self, *, summary_text: str, output_format: str, filename_stem: str) -> CreatedDocument:
        return await self._inner.create(summary_text=summary_text, output_format=output_format, filename_stem=filename_stem)


class TracedTTSProvider(TTSProviderPort):
    def __init__(self, inner: TTSProviderPort) -> None:
        self._inner = inner

    @metered_sync("adapter.tts_provider", "synthesize")
    @traced_sync(
        "adapter.tts_provider.synthesize",
        attribute_builder=lambda self, text, audio_format: {"text.length": len(text), "audio.format": audio_format},
    )
    def synthesize(self, text: str, audio_format: str) -> bytes:
        return self._inner.synthesize(text, audio_format)


class TracedImageProvider(ImageProviderPort):
    def __init__(self, inner: ImageProviderPort) -> None:
        self._inner = inner

    @metered_sync("adapter.image_provider", "generate_from_text")
    @traced_sync(
        "adapter.image_provider.generate_from_text",
        attribute_builder=lambda self, text: {"text.length": len(text)},
    )
    def generate_from_text(self, text: str) -> dict:
        return self._inner.generate_from_text(text)

