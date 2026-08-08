"""Module `src/document_analyzer_api/api/routes/documents.py`.

This module belongs to the API routing layer of Document Analyzer.

Purpose:
- Adapts HTTP input/output contracts to application-service calls.

Defined symbols:
- Classes: none.
- Functions: _parse_chunking_options, _to_domain_chunking_config, _validate_upload_count, _validate_file_size, _validate_total_size, _to_api_result, ingest_documents, list_documents, documents_capabilities, generate_document_answer, create_documents_summary, create_chat_session, delete_chat_session, chat_documents, _ollama_style_stream, _resolve_text_answer, _audio_response_from_generate.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import json
from typing import AsyncGenerator

from fastapi import APIRouter, File, Form, Query, Request, UploadFile, status
from fastapi.responses import JSONResponse, Response, StreamingResponse

from ...application.services.document_ingestion_service import IngestionResult
from ...domain.models.chunking import ChunkGranularity as DomainChunkGranularity
from ...domain.models.chunking import ChunkingConfig, ChunkingStrategyName
from ...domain.models.chunking import DEFAULT_CONTEXTUAL_SUMMARY_PROMPT
from ...domain.ports.document_storage import UploadedFileData
from ...observability.metrics import metered_async
from ...observability.tracing import traced_async
from ..schemas.generation import (
    ChatSessionCreateResponse,
    DocumentChatRequest,
    DocumentChatResponse,
    DocumentGenerateRequest,
    DocumentGenerateResponse,
    DocumentSummaryRequest,
    DocumentSummaryResponse,
)
from ..errors import ValidationProblem
from ..schemas.documents import (
    DocumentCapabilitiesResponse,
    ChunkingOptions,
    DocumentIngestFileStatus,
    DocumentIngestResponse,
    DocumentIngestResult,
    DocumentListItem,
    DocumentListResponse,
)

router = APIRouter(tags=["documents"])


@router.post("/documents", response_model=DocumentIngestResponse)
@traced_async("operation.documents.ingest", attribute_builder=lambda request, files, chunking=None: {"files.count": len(files)})
@metered_async("operation.documents", "ingest")
async def ingest_documents(
    request: Request,
    files: list[UploadFile] = File(...),
    chunking: str | None = Form(default=None),
) -> JSONResponse:
    """Asynchronous execution path for `ingest_documents`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (DocumentIngestResponse, File, Form, JSONResponse) to satisfy the callable contract.
    
        Args:
            request: Incoming HTTP request carrying route/query/body/context data.
            files: Input parameter accepted by `ingest_documents`.
            chunking: Input parameter accepted by `ingest_documents`.
    
        Returns:
            A value compatible with `JSONResponse`.
    """
    if not files:
        raise ValidationProblem(detail="At least one file is required")

    chunking_options = _parse_chunking_options(chunking)
    settings = request.app.state.container.settings
    _validate_upload_count(len(files), settings.max_files_per_request)

    uploaded_files: list[UploadedFileData] = []
    total_payload = 0
    for item in files:
        content = await item.read()
        _validate_file_size(len(content), settings.max_file_size_bytes, item.filename or "unknown")
        total_payload += len(content)
        uploaded_files.append(UploadedFileData(name=item.filename or "unknown", content=content))

    _validate_total_size(total_payload, settings.max_total_payload_bytes)

    chunking_config = _to_domain_chunking_config(chunking_options)
    ingestion_results = await request.app.state.container.ingestion_service.ingest_files(
        uploaded_files,
        chunking_config,
    )
    response = DocumentIngestResponse(results=[_to_api_result(item) for item in ingestion_results])
    all_ok = all(item.ok for item in ingestion_results)
    response_code = status.HTTP_200_OK if all_ok else status.HTTP_207_MULTI_STATUS
    return JSONResponse(status_code=response_code, content=response.model_dump())


@router.get("/documents", response_model=DocumentListResponse)
@traced_async(
    "operation.documents.list",
    attribute_builder=lambda request, offset=0, limit=50: {"pagination.offset": offset, "pagination.limit": limit},
)
@metered_async("operation.documents", "list")
async def list_documents(
    request: Request,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1),
) -> DocumentListResponse:
    """Asynchronous execution path for `list_documents`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Collects and returns a list or paginated subset of entities.
    
        Args:
            request: Incoming HTTP request carrying route/query/body/context data.
            offset: Input parameter accepted by `list_documents`.
            limit: Input parameter accepted by `list_documents`.
    
        Returns:
            A value compatible with `DocumentListResponse`.
    """
    items, total = await request.app.state.container.document_query_service.list_documents(offset=offset, limit=limit)
    return DocumentListResponse(
        items=[DocumentListItem(id=item.id, name=item.name, description=item.description) for item in items],
        offset=offset,
        limit=limit,
        total=total,
    )


@router.get("/documents/capabilities", response_model=DocumentCapabilitiesResponse)
@traced_async("operation.documents.capabilities")
@metered_async("operation.documents", "capabilities")
async def documents_capabilities(request: Request) -> DocumentCapabilitiesResponse:
    """Asynchronous execution path for `documents_capabilities`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (DocumentCapabilitiesResponse, get, list) to satisfy the callable contract.
    
        Args:
            request: Incoming HTTP request carrying route/query/body/context data.
    
        Returns:
            A value compatible with `DocumentCapabilitiesResponse`.
    """
    ingestion_service = request.app.state.container.ingestion_service
    summary_service = request.app.state.container.summary_service
    return DocumentCapabilitiesResponse(
        supportedInputExtensions=list(ingestion_service.supported_extensions),
        supportedSummaryOutputFormats=list(summary_service.supported_output_formats),
    )


@router.post("/documents/generate", response_model=None)
@traced_async(
    "operation.documents.generate",
    attribute_builder=lambda request, payload: {
        "output.format": payload.outputFormat.value,
        "retrieval.mode": payload.retrievalMode.value,
        "stream": payload.stream,
    },
)
@metered_async("operation.documents", "generate")
async def generate_document_answer(
    request: Request,
    payload: DocumentGenerateRequest,
) -> Response | JSONResponse | StreamingResponse:
    """Asynchronous execution path for `generate_document_answer`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Generates derived output from context, prompts, and generation options.
    
        Args:
            request: Incoming HTTP request carrying route/query/body/context data.
            payload: Input parameter accepted by `generate_document_answer`.
    
        Returns:
            A value compatible with `Response | JSONResponse | StreamingResponse`.
    """
    if payload.outputFormat.value == "audio":
        return await _audio_response_from_generate(request, payload)

    if payload.outputFormat.value == "image":
        answer, image_payload, citations = await request.app.state.container.image_service.generate_image_answer(
            question=payload.question,
            document_ids=payload.documentIds,
            keywords=payload.keywords,
            keywords_mode=payload.keywordsMode.value,
            retrieval_mode=payload.retrievalMode.value,
            top_k=payload.retrievalOptions.common.topK,
            min_score=payload.retrievalOptions.common.minScore,
            hybrid_alpha=payload.retrievalOptions.hybrid.hybridAlpha,
            include_sources=payload.includeSources,
            graph_max_hops=payload.retrievalOptions.graph.maxHops,
        )
        return JSONResponse(status_code=200, content={"answer": answer, "citations": citations, "image": image_payload})

    if payload.outputFormat.value == "text+image":
        answer, image_payload, citations = await request.app.state.container.image_service.generate_image_answer(
            question=payload.question,
            document_ids=payload.documentIds,
            keywords=payload.keywords,
            keywords_mode=payload.keywordsMode.value,
            retrieval_mode=payload.retrievalMode.value,
            top_k=payload.retrievalOptions.common.topK,
            min_score=payload.retrievalOptions.common.minScore,
            hybrid_alpha=payload.retrievalOptions.hybrid.hybridAlpha,
            include_sources=payload.includeSources,
            graph_max_hops=payload.retrievalOptions.graph.maxHops,
        )
        return JSONResponse(status_code=200, content={"answer": answer, "citations": citations, "image": image_payload})

    answer, citations = await _resolve_text_answer(request, payload)

    if payload.stream:
        return StreamingResponse(
            _ollama_style_stream(answer),
            media_type="application/x-ndjson",
        )

    return JSONResponse(
        status_code=200,
        content=DocumentGenerateResponse(answer=answer, citations=citations).model_dump(),
    )


@router.post("/documents/summary", response_model=DocumentSummaryResponse, response_model_exclude_none=True)
@traced_async(
    "operation.documents.summary",
    attribute_builder=lambda request, payload: {
        "output.format": payload.outputFormat,
        "documents.count": len(payload.documentIds or []),
        "retrieval.mode": payload.retrievalMode.value,
        "summary.word_count": payload.summaryWordCount or 0,
        "summary.has_custom_prompt": bool(payload.summaryPrompt),
        "summary.include_inline": payload.includeSummary,
    },
)
@metered_async("operation.documents", "summary")
async def create_documents_summary(
    request: Request,
    payload: DocumentSummaryRequest,
) -> DocumentSummaryResponse:
    """Asynchronous execution path for `create_documents_summary`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Creates a resource and returns identifiers or materialized result payloads.
    
        Args:
            request: Incoming HTTP request carrying route/query/body/context data.
            payload: Input parameter accepted by `create_documents_summary`.
    
        Returns:
            A value compatible with `DocumentSummaryResponse`.
    """
    supported_output_formats = request.app.state.container.summary_service.supported_output_formats
    normalized_output = payload.outputFormat.lower()
    if normalized_output not in supported_output_formats:
        supported_values = ", ".join(supported_output_formats)
        raise ValidationProblem(
            detail=f"Unsupported outputFormat '{payload.outputFormat}'. Supported values: {supported_values}"
        )

    url, summary_text = await request.app.state.container.summary_service.create_summary(
        document_ids=payload.documentIds,
        keywords=payload.keywords,
        keywords_mode=payload.keywordsMode.value,
        retrieval_mode=payload.retrievalMode.value,
        top_k=payload.retrievalOptions.common.topK,
        min_score=payload.retrievalOptions.common.minScore,
        hybrid_alpha=payload.retrievalOptions.hybrid.hybridAlpha,
        graph_max_hops=payload.retrievalOptions.graph.maxHops,
        summary_word_count=payload.summaryWordCount,
        summary_prompt=payload.summaryPrompt,
        output_format=normalized_output,
    )
    inline_summary = summary_text if payload.includeSummary else None
    return DocumentSummaryResponse(url=url, summaryText=inline_summary)


@router.post("/chat/sessions", response_model=ChatSessionCreateResponse)
@traced_async("operation.chat.create_session")
@metered_async("operation.chat", "create_session")
async def create_chat_session(request: Request) -> ChatSessionCreateResponse:
    """Asynchronous execution path for `create_chat_session`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Creates a resource and returns identifiers or materialized result payloads.
    
        Args:
            request: Incoming HTTP request carrying route/query/body/context data.
    
        Returns:
            A value compatible with `ChatSessionCreateResponse`.
    """
    session_id = await request.app.state.container.chat_service.create_session()
    return ChatSessionCreateResponse(sessionId=session_id)


@router.delete("/chat/sessions/{session_id}")
@traced_async("operation.chat.delete_session", attribute_builder=lambda request, session_id: {"session_id": session_id})
@metered_async("operation.chat", "delete_session")
async def delete_chat_session(request: Request, session_id: str) -> JSONResponse:
    """Asynchronous execution path for `delete_chat_session`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Deletes a target resource and reports outcome deterministically.
    
        Args:
            request: Incoming HTTP request carrying route/query/body/context data.
            session_id: Server-side chat session identifier.
    
        Returns:
            A value compatible with `JSONResponse`.
    """
    deleted = await request.app.state.container.chat_service.delete_session(session_id)
    status_code = status.HTTP_200_OK if deleted else status.HTTP_404_NOT_FOUND
    return JSONResponse(status_code=status_code, content={"deleted": deleted})


@router.post("/documents/chat", response_model=None)
@traced_async(
    "operation.documents.chat",
    attribute_builder=lambda request, payload: {
        "session_id": payload.sessionId,
        "output.format": payload.outputFormat.value,
        "retrieval.mode": payload.retrievalMode.value,
        "stream": payload.stream,
    },
)
@metered_async("operation.documents", "chat")
async def chat_documents(
    request: Request,
    payload: DocumentChatRequest,
) -> Response | JSONResponse | StreamingResponse:
    """Asynchronous execution path for `chat_documents`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Runs stateful chat logic with persisted context and new user input.
    
        Args:
            request: Incoming HTTP request carrying route/query/body/context data.
            payload: Input parameter accepted by `chat_documents`.
    
        Returns:
            A value compatible with `Response | JSONResponse | StreamingResponse`.
    """
    try:
        answer, citations = await request.app.state.container.chat_service.chat(
            session_id=payload.sessionId,
            question=payload.question,
            document_ids=payload.documentIds,
            keywords=payload.keywords,
            keywords_mode=payload.keywordsMode.value,
            retrieval_mode=payload.retrievalMode.value,
            top_k=payload.retrievalOptions.common.topK,
            min_score=payload.retrievalOptions.common.minScore,
            hybrid_alpha=payload.retrievalOptions.hybrid.hybridAlpha,
            include_sources=payload.includeSources,
            graph_max_hops=payload.retrievalOptions.graph.maxHops,
            compact_context=payload.compactContext,
        )
    except ValueError as exc:
        raise ValidationProblem(detail=str(exc)) from exc

    if payload.outputFormat.value == "audio":
        audio_bytes = request.app.state.container.audio_service.render_audio(
            text=answer,
            audio_format=request.app.state.container.settings.default_audio_format,
        )
        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=answer.wav"},
        )

    if payload.outputFormat.value in {"image", "text+image"}:
        image_payload = request.app.state.container.image_service.render_image(answer)
        return JSONResponse(
            status_code=200,
            content={"answer": answer, "citations": citations, "sessionId": payload.sessionId, "image": image_payload},
        )

    if payload.stream:
        return StreamingResponse(_ollama_style_stream(answer), media_type="application/x-ndjson")

    return JSONResponse(
        status_code=200,
        content=DocumentChatResponse(answer=answer, citations=citations, sessionId=payload.sessionId).model_dump(),
    )


def _parse_chunking_options(chunking: str | None) -> ChunkingOptions:
    """Synchronous execution path for `_parse_chunking_options`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (ChunkingOptions, ValidationProblem, loads, model_validate) to satisfy the callable contract.
    
        Args:
            chunking: Input parameter accepted by `_parse_chunking_options`.
    
        Returns:
            A value compatible with `ChunkingOptions`.
    """
    if not chunking:
        return ChunkingOptions()

    try:
        chunking_options = ChunkingOptions.model_validate(json.loads(chunking))
    except json.JSONDecodeError as exc:
        raise ValidationProblem(detail="chunking field must be valid JSON") from exc

    if chunking_options.granularity.value != "sub_paragraph_tokens" and chunking_options.subParagraph is not None:
        raise ValidationProblem(detail="subParagraph can only be used with granularity=sub_paragraph_tokens")

    contextual_options = None
    if chunking_options.strategyOptions is not None:
        contextual_options = chunking_options.strategyOptions.contextualSummary

    if chunking_options.strategy.value != "contextual_summary" and contextual_options is not None:
        raise ValidationProblem(
            detail="strategyOptions.contextualSummary can only be used with strategy=contextual_summary"
        )

    return chunking_options


def _to_domain_chunking_config(chunking_options: ChunkingOptions) -> ChunkingConfig:
    """Synchronous execution path for `_to_domain_chunking_config`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (ChunkingConfig, ChunkingStrategyName, DomainChunkGranularity) to satisfy the callable contract.
    
        Args:
            chunking_options: Input parameter accepted by `_to_domain_chunking_config`.
    
        Returns:
            A value compatible with `ChunkingConfig`.
    """
    prompt = DEFAULT_CONTEXTUAL_SUMMARY_PROMPT
    if chunking_options.strategyOptions and chunking_options.strategyOptions.contextualSummary:
        prompt = chunking_options.strategyOptions.contextualSummary.prompt

    target_tokens = 350
    overlap_tokens = 60
    if chunking_options.subParagraph:
        target_tokens = chunking_options.subParagraph.targetTokens
        overlap_tokens = chunking_options.subParagraph.overlapTokens

    return ChunkingConfig(
        strategy=ChunkingStrategyName(chunking_options.strategy.value),
        granularity=DomainChunkGranularity(chunking_options.granularity.value),
        target_tokens=target_tokens,
        overlap_tokens=overlap_tokens,
        contextual_summary_prompt=prompt,
    )


def _validate_upload_count(files_count: int, max_files_per_request: int) -> None:
    """Synchronous execution path for `_validate_upload_count`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (ValidationProblem) to satisfy the callable contract.
    
        Args:
            files_count: Input parameter accepted by `_validate_upload_count`.
            max_files_per_request: Input parameter accepted by `_validate_upload_count`.
    
        Returns:
            A value compatible with `None`.
    """
    if max_files_per_request > 0 and files_count > max_files_per_request:
        raise ValidationProblem(detail=f"Too many files in request; max is {max_files_per_request}")


def _validate_file_size(file_size: int, max_file_size_bytes: int, file_name: str) -> None:
    """Synchronous execution path for `_validate_file_size`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (ValidationProblem) to satisfy the callable contract.
    
        Args:
            file_size: Input parameter accepted by `_validate_file_size`.
            max_file_size_bytes: Input parameter accepted by `_validate_file_size`.
            file_name: Input parameter accepted by `_validate_file_size`.
    
        Returns:
            A value compatible with `None`.
    """
    if max_file_size_bytes > 0 and file_size > max_file_size_bytes:
        raise ValidationProblem(detail=f"File '{file_name}' exceeds max allowed size")


def _validate_total_size(total_payload: int, max_total_payload_bytes: int) -> None:
    """Synchronous execution path for `_validate_total_size`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (ValidationProblem) to satisfy the callable contract.
    
        Args:
            total_payload: Input parameter accepted by `_validate_total_size`.
            max_total_payload_bytes: Input parameter accepted by `_validate_total_size`.
    
        Returns:
            A value compatible with `None`.
    """
    if max_total_payload_bytes > 0 and total_payload > max_total_payload_bytes:
        raise ValidationProblem(detail="Total payload exceeds max allowed size")


def _to_api_result(item: IngestionResult) -> DocumentIngestResult:
    """Synchronous execution path for `_to_api_result`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (DocumentIngestFileStatus, DocumentIngestResult) to satisfy the callable contract.
    
        Args:
            item: Input parameter accepted by `_to_api_result`.
    
        Returns:
            A value compatible with `DocumentIngestResult`.
    """
    error_code = None
    if item.status.value == "conflict":
        error_code = "CONFLICT"
    elif item.status.value == "unsupported_media_type":
        error_code = "UNSUPPORTED_MEDIA_TYPE"
    elif item.status.value == "failed":
        error_code = "INGESTION_FAILED"

    return DocumentIngestResult(
        name=item.name,
        status=DocumentIngestFileStatus(item.status.value),
        documentId=item.document_id,
        errorCode=error_code,
        error=item.error,
    )


async def _ollama_style_stream(answer: str) -> AsyncGenerator[bytes, None]:
    """Asynchronous execution path for `_ollama_style_stream`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (dumps, encode, split) to satisfy the callable contract.
    
        Args:
            answer: Input parameter accepted by `_ollama_style_stream`.
    
        Returns:
            A value compatible with `AsyncGenerator[bytes, None]`.
    """
    words = answer.split(" ")
    for word in words:
        payload = {"response": f"{word} ", "done": False}
        yield (json.dumps(payload) + "\n").encode("utf-8")
    yield (json.dumps({"response": "", "done": True}) + "\n").encode("utf-8")


async def _resolve_text_answer(request: Request, payload: DocumentGenerateRequest | DocumentChatRequest) -> tuple[str, list[dict]]:
    """Asynchronous execution path for `_resolve_text_answer`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (generate) to satisfy the callable contract.
    
        Args:
            request: Incoming HTTP request carrying route/query/body/context data.
            payload: Input parameter accepted by `_resolve_text_answer`.
    
        Returns:
            A value compatible with `tuple[str, list[dict]]`.
    """
    return await request.app.state.container.generation_service.generate(
        question=payload.question,
        document_ids=payload.documentIds,
        keywords=payload.keywords,
        keywords_mode=payload.keywordsMode.value,
        retrieval_mode=payload.retrievalMode.value,
        top_k=payload.retrievalOptions.common.topK,
        min_score=payload.retrievalOptions.common.minScore,
        hybrid_alpha=payload.retrievalOptions.hybrid.hybridAlpha,
        include_sources=payload.includeSources,
        graph_max_hops=payload.retrievalOptions.graph.maxHops,
    )


async def _audio_response_from_generate(request: Request, payload: DocumentGenerateRequest) -> Response:
    """Asynchronous execution path for `_audio_response_from_generate`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (Response, generate_audio_answer) to satisfy the callable contract.
    
        Args:
            request: Incoming HTTP request carrying route/query/body/context data.
            payload: Input parameter accepted by `_audio_response_from_generate`.
    
        Returns:
            A value compatible with `Response`.
    """
    audio_bytes, _ = await request.app.state.container.audio_service.generate_audio_answer(
        question=payload.question,
        document_ids=payload.documentIds,
        keywords=payload.keywords,
        keywords_mode=payload.keywordsMode.value,
        retrieval_mode=payload.retrievalMode.value,
        top_k=payload.retrievalOptions.common.topK,
        min_score=payload.retrievalOptions.common.minScore,
        hybrid_alpha=payload.retrievalOptions.hybrid.hybridAlpha,
        include_sources=payload.includeSources,
        graph_max_hops=payload.retrievalOptions.graph.maxHops,
        audio_format=request.app.state.container.settings.default_audio_format,
    )
    return Response(
        content=audio_bytes,
        media_type="audio/wav",
        headers={"Content-Disposition": "attachment; filename=answer.wav"},
    )









