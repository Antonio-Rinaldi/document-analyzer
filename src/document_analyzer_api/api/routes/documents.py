"""Detailed module documentation for `src/document_analyzer_api/api/routes/documents.py`.

File role:
- Located in the API routing layer.
- Defines logic and symbols for `documents.py` within Document Analyzer V1.

Purpose:
- Implements HTTP endpoint handlers and translates transport payloads into service calls.

Exported symbols overview:
- Classes: none.
- Functions: ingest_documents, list_documents, documents_capabilities, generate_document_answer, create_documents_summary, create_chat_session, delete_chat_session, chat_documents, _parse_chunking_options, _to_domain_chunking_config, _validate_upload_count, _validate_file_size, _validate_total_size, _to_api_result, _ollama_style_stream, _resolve_text_answer, _audio_response_from_generate.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
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
async def ingest_documents(
    request: Request,
    files: list[UploadFile] = File(...),
    chunking: str | None = Form(default=None),
) -> JSONResponse:
    """Detailed asynchronous function documentation for `ingest_documents`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            request: Incoming request object carrying path/query/body/context information.
            files: Input parameter for `ingest_documents`.
            chunking: Input parameter for `ingest_documents`.
    
        Returns:
            Value defined by `ingest_documents` contract and consumed by downstream callers.
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
async def list_documents(
    request: Request,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1),
) -> DocumentListResponse:
    """Detailed asynchronous function documentation for `list_documents`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Collects and returns a paginated or aggregated list of entities.
    
        Args:
            request: Incoming request object carrying path/query/body/context information.
            offset: Input parameter for `list_documents`.
            limit: Input parameter for `list_documents`.
    
        Returns:
            Value defined by `list_documents` contract and consumed by downstream callers.
    """
    items, total = await request.app.state.container.document_query_service.list_documents(offset=offset, limit=limit)
    return DocumentListResponse(
        items=[DocumentListItem(id=item.id, name=item.name, description=item.description) for item in items],
        offset=offset,
        limit=limit,
        total=total,
    )


@router.get("/documents/capabilities", response_model=DocumentCapabilitiesResponse)
async def documents_capabilities(request: Request) -> DocumentCapabilitiesResponse:
    """Detailed asynchronous function documentation for `documents_capabilities`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            request: Incoming request object carrying path/query/body/context information.
    
        Returns:
            Value defined by `documents_capabilities` contract and consumed by downstream callers.
    """
    ingestion_service = request.app.state.container.ingestion_service
    summary_service = request.app.state.container.summary_service
    return DocumentCapabilitiesResponse(
        supportedInputExtensions=list(ingestion_service.supported_extensions),
        supportedSummaryOutputFormats=list(summary_service.supported_output_formats),
    )


@router.post("/documents/generate", response_model=None)
async def generate_document_answer(
    request: Request,
    payload: DocumentGenerateRequest,
) -> Response | JSONResponse | StreamingResponse:
    """Detailed asynchronous function documentation for `generate_document_answer`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Generates derived output from retrieved context and provided options.
    
        Args:
            request: Incoming request object carrying path/query/body/context information.
            payload: Input parameter for `generate_document_answer`.
    
        Returns:
            Value defined by `generate_document_answer` contract and consumed by downstream callers.
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


@router.post("/documents/summary", response_model=DocumentSummaryResponse)
async def create_documents_summary(
    request: Request,
    payload: DocumentSummaryRequest,
) -> DocumentSummaryResponse:
    """Detailed asynchronous function documentation for `create_documents_summary`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Creates a new resource and returns identifiers or resulting payloads.
    
        Args:
            request: Incoming request object carrying path/query/body/context information.
            payload: Input parameter for `create_documents_summary`.
    
        Returns:
            Value defined by `create_documents_summary` contract and consumed by downstream callers.
    """
    supported_output_formats = request.app.state.container.summary_service.supported_output_formats
    normalized_output = payload.outputFormat.lower()
    if normalized_output not in supported_output_formats:
        supported_values = ", ".join(supported_output_formats)
        raise ValidationProblem(
            detail=f"Unsupported outputFormat '{payload.outputFormat}'. Supported values: {supported_values}"
        )

    url = await request.app.state.container.summary_service.create_summary(
        document_ids=payload.documentIds,
        keywords=payload.keywords,
        output_format=normalized_output,
    )
    return DocumentSummaryResponse(url=url)


@router.post("/chat/sessions", response_model=ChatSessionCreateResponse)
async def create_chat_session(request: Request) -> ChatSessionCreateResponse:
    """Detailed asynchronous function documentation for `create_chat_session`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Creates a new resource and returns identifiers or resulting payloads.
    
        Args:
            request: Incoming request object carrying path/query/body/context information.
    
        Returns:
            Value defined by `create_chat_session` contract and consumed by downstream callers.
    """
    session_id = await request.app.state.container.chat_service.create_session()
    return ChatSessionCreateResponse(sessionId=session_id)


@router.delete("/chat/sessions/{session_id}")
async def delete_chat_session(request: Request, session_id: str) -> JSONResponse:
    """Detailed asynchronous function documentation for `delete_chat_session`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Deletes a resource and reports whether deletion succeeded.
    
        Args:
            request: Incoming request object carrying path/query/body/context information.
            session_id: Server-side chat session identifier.
    
        Returns:
            Value defined by `delete_chat_session` contract and consumed by downstream callers.
    """
    deleted = await request.app.state.container.chat_service.delete_session(session_id)
    status_code = status.HTTP_200_OK if deleted else status.HTTP_404_NOT_FOUND
    return JSONResponse(status_code=status_code, content={"deleted": deleted})


@router.post("/documents/chat", response_model=None)
async def chat_documents(
    request: Request,
    payload: DocumentChatRequest,
) -> Response | JSONResponse | StreamingResponse:
    """Detailed asynchronous function documentation for `chat_documents`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes stateful chat logic using persisted session context.
    
        Args:
            request: Incoming request object carrying path/query/body/context information.
            payload: Input parameter for `chat_documents`.
    
        Returns:
            Value defined by `chat_documents` contract and consumed by downstream callers.
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
    """Detailed synchronous function documentation for `_parse_chunking_options`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            chunking: Input parameter for `_parse_chunking_options`.
    
        Returns:
            Value defined by `_parse_chunking_options` contract and consumed by downstream callers.
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
    """Detailed synchronous function documentation for `_to_domain_chunking_config`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            chunking_options: Input parameter for `_to_domain_chunking_config`.
    
        Returns:
            Value defined by `_to_domain_chunking_config` contract and consumed by downstream callers.
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
    """Detailed synchronous function documentation for `_validate_upload_count`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            files_count: Input parameter for `_validate_upload_count`.
            max_files_per_request: Input parameter for `_validate_upload_count`.
    
        Returns:
            Value defined by `_validate_upload_count` contract and consumed by downstream callers.
    """
    if max_files_per_request > 0 and files_count > max_files_per_request:
        raise ValidationProblem(detail=f"Too many files in request; max is {max_files_per_request}")


def _validate_file_size(file_size: int, max_file_size_bytes: int, file_name: str) -> None:
    """Detailed synchronous function documentation for `_validate_file_size`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            file_size: Input parameter for `_validate_file_size`.
            max_file_size_bytes: Input parameter for `_validate_file_size`.
            file_name: Input parameter for `_validate_file_size`.
    
        Returns:
            Value defined by `_validate_file_size` contract and consumed by downstream callers.
    """
    if max_file_size_bytes > 0 and file_size > max_file_size_bytes:
        raise ValidationProblem(detail=f"File '{file_name}' exceeds max allowed size")


def _validate_total_size(total_payload: int, max_total_payload_bytes: int) -> None:
    """Detailed synchronous function documentation for `_validate_total_size`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            total_payload: Input parameter for `_validate_total_size`.
            max_total_payload_bytes: Input parameter for `_validate_total_size`.
    
        Returns:
            Value defined by `_validate_total_size` contract and consumed by downstream callers.
    """
    if max_total_payload_bytes > 0 and total_payload > max_total_payload_bytes:
        raise ValidationProblem(detail="Total payload exceeds max allowed size")


def _to_api_result(item: IngestionResult) -> DocumentIngestResult:
    """Detailed synchronous function documentation for `_to_api_result`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            item: Input parameter for `_to_api_result`.
    
        Returns:
            Value defined by `_to_api_result` contract and consumed by downstream callers.
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
    """Detailed asynchronous function documentation for `_ollama_style_stream`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            answer: Input parameter for `_ollama_style_stream`.
    
        Returns:
            Value defined by `_ollama_style_stream` contract and consumed by downstream callers.
    """
    words = answer.split(" ")
    for word in words:
        payload = {"response": f"{word} ", "done": False}
        yield (json.dumps(payload) + "\n").encode("utf-8")
    yield (json.dumps({"response": "", "done": True}) + "\n").encode("utf-8")


async def _resolve_text_answer(request: Request, payload: DocumentGenerateRequest | DocumentChatRequest) -> tuple[str, list[dict]]:
    """Detailed asynchronous function documentation for `_resolve_text_answer`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            request: Incoming request object carrying path/query/body/context information.
            payload: Input parameter for `_resolve_text_answer`.
    
        Returns:
            Value defined by `_resolve_text_answer` contract and consumed by downstream callers.
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
    )


async def _audio_response_from_generate(request: Request, payload: DocumentGenerateRequest) -> Response:
    """Detailed asynchronous function documentation for `_audio_response_from_generate`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/documents.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            request: Incoming request object carrying path/query/body/context information.
            payload: Input parameter for `_audio_response_from_generate`.
    
        Returns:
            Value defined by `_audio_response_from_generate` contract and consumed by downstream callers.
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
        audio_format=request.app.state.container.settings.default_audio_format,
    )
    return Response(
        content=audio_bytes,
        media_type="audio/wav",
        headers={"Content-Disposition": "attachment; filename=answer.wav"},
    )









