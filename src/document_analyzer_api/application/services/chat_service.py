"""Module `src/document_analyzer_api/application/services/chat_service.py`.

This module belongs to the application service layer of Document Analyzer.

Purpose:
- Coordinates use-case workflows over domain ports and adapters.

Defined symbols:
- Classes: ChatService.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import uuid

from ...domain.models.chat import ChatMessage, ChatRole
from ...domain.ports.chat_session_repository import ChatSessionRepositoryPort
from .document_generation_service import DocumentGenerationService


class ChatService:
    """ChatService application service.
    
    This class is defined in `src/document_analyzer_api/application/services/chat_service.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(
        self,
        *,
        repository: ChatSessionRepositoryPort,
        generation_service: DocumentGenerationService,
        chat_ttl_seconds: int,
        max_messages_before_compaction: int,
    ) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/chat_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Executes the callable contract for this module concern.
        
            Args:
                repository: Input parameter accepted by `__init__`.
                generation_service: Input parameter accepted by `__init__`.
                chat_ttl_seconds: Input parameter accepted by `__init__`.
                max_messages_before_compaction: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._repository = repository
        self._generation_service = generation_service
        self._chat_ttl_seconds = chat_ttl_seconds
        self._max_messages_before_compaction = max_messages_before_compaction

    async def create_session(self) -> str:
        """Asynchronous execution path for `create_session`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/chat_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Creates a resource and returns identifiers or materialized result payloads.
        
            Args:
                None.
        
            Returns:
                A value compatible with `str`.
        """
        session_id = uuid.uuid4().hex
        await self._repository.create(session_id=session_id, ttl_seconds=self._chat_ttl_seconds)
        return session_id

    async def delete_session(self, session_id: str) -> bool:
        """Asynchronous execution path for `delete_session`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/chat_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Deletes a target resource and reports outcome deterministically.
        
            Args:
                session_id: Server-side chat session identifier.
        
            Returns:
                A value compatible with `bool`.
        """
        return await self._repository.delete(session_id)

    async def chat(
        self,
        *,
        session_id: str,
        question: str,
        document_ids: list[str] | None,
        keywords: list[str],
        keywords_mode: str,
        retrieval_mode: str,
        top_k: int,
        min_score: float,
        hybrid_alpha: float,
        include_sources: bool,
        compact_context: bool,
    ) -> tuple[str, list[dict]]:
        """Asynchronous execution path for `chat`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/chat_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Runs stateful chat logic with persisted context and new user input.
        
            Args:
                session_id: Server-side chat session identifier.
                question: User prompt processed by retrieval and generation workflows.
                document_ids: Optional subset of documents used to scope the operation.
                keywords: Optional keyword list used for retrieval metadata/filtering/boosting.
                keywords_mode: Keyword strategy selector (`metadata_only`, `filter`, `rank_boost`).
                retrieval_mode: Retrieval backend mode (`vector`, `graph`, or `hybrid`).
                top_k: Maximum number of retrieval hits retained for context assembly.
                min_score: Minimum score threshold used to discard low-confidence hits.
                hybrid_alpha: Fusion weight for hybrid retrieval blending.
                include_sources: Flag controlling citation extraction in response payloads.
                compact_context: Flag requesting immediate context compaction in chat flows.
        
            Returns:
                A value compatible with `tuple[str, list[dict]]`.
        """
        session = await self._repository.get(session_id)
        if session is None:
            raise ValueError("Session not found")

        session.messages.append(ChatMessage(role=ChatRole.user, content=question))

        if compact_context or len(session.messages) > self._max_messages_before_compaction:
            session.messages = self._compact_messages(session.messages)

        answer, citations = await self._generation_service.generate(
            question=question,
            document_ids=document_ids,
            keywords=keywords,
            keywords_mode=keywords_mode,
            retrieval_mode=retrieval_mode,
            top_k=top_k,
            min_score=min_score,
            hybrid_alpha=hybrid_alpha,
            include_sources=include_sources,
        )

        session.messages.append(ChatMessage(role=ChatRole.assistant, content=answer))
        await self._repository.upsert(session, ttl_seconds=self._chat_ttl_seconds)
        return answer, citations

    def _compact_messages(self, messages: list[ChatMessage]) -> list[ChatMessage]:
        """Synchronous execution path for `_compact_messages`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/chat_service.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (ChatMessage, join, len) to satisfy the callable contract.
        
            Args:
                messages: Input parameter accepted by `_compact_messages`.
        
            Returns:
                A value compatible with `list[ChatMessage]`.
        """
        if len(messages) <= 2:
            return messages

        old_messages = messages[:-2]
        recent_messages = messages[-2:]
        summary = " ".join(message.content for message in old_messages)
        compacted = ChatMessage(role=ChatRole.system, content=f"Context summary: {summary[:500]}")
        return [compacted, *recent_messages]


