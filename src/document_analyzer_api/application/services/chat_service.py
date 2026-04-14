"""Detailed module documentation for `src/document_analyzer_api/application/services/chat_service.py`.

File role:
- Located in the application service layer.
- Defines logic and symbols for `chat_service.py` within Document Analyzer V1.

Purpose:
- Implements use-case orchestration across domain ports and infrastructure adapters.

Exported symbols overview:
- Classes: ChatService.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

import uuid

from ...domain.models.chat import ChatMessage, ChatRole
from ...domain.ports.chat_session_repository import ChatSessionRepositoryPort
from .document_generation_service import DocumentGenerationService


class ChatService:
    """Detailed class documentation for `ChatService`.
    
    This application service belongs to `src/document_analyzer_api/application/services/chat_service.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(
        self,
        *,
        repository: ChatSessionRepositoryPort,
        generation_service: DocumentGenerationService,
        chat_ttl_seconds: int,
        max_messages_before_compaction: int,
    ) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/chat_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                repository: Input parameter for `__init__`.
                generation_service: Input parameter for `__init__`.
                chat_ttl_seconds: Input parameter for `__init__`.
                max_messages_before_compaction: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._repository = repository
        self._generation_service = generation_service
        self._chat_ttl_seconds = chat_ttl_seconds
        self._max_messages_before_compaction = max_messages_before_compaction

    async def create_session(self) -> str:
        """Detailed asynchronous function documentation for `create_session`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/chat_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Creates a new resource and returns identifiers or resulting payloads.
        
            Args:
                None.
        
            Returns:
                Value defined by `create_session` contract and consumed by downstream callers.
        """
        session_id = uuid.uuid4().hex
        await self._repository.create(session_id=session_id, ttl_seconds=self._chat_ttl_seconds)
        return session_id

    async def delete_session(self, session_id: str) -> bool:
        """Detailed asynchronous function documentation for `delete_session`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/chat_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Deletes a resource and reports whether deletion succeeded.
        
            Args:
                session_id: Server-side chat session identifier.
        
            Returns:
                Value defined by `delete_session` contract and consumed by downstream callers.
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
        """Detailed asynchronous function documentation for `chat`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/chat_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes stateful chat logic using persisted session context.
        
            Args:
                session_id: Server-side chat session identifier.
                question: User question or prompt text to process.
                document_ids: Optional subset of document identifiers to scope the operation.
                keywords: Optional keyword list used by retrieval behavior.
                keywords_mode: Retrieval keyword strategy selector.
                retrieval_mode: Retrieval backend mode (`vector`, `graph`, or `hybrid`).
                top_k: Maximum number of retrieved items considered in downstream steps.
                min_score: Minimum score threshold used to accept retrieval hits.
                hybrid_alpha: Fusion weight used when hybrid retrieval mode is selected.
                include_sources: Flag controlling citation/source emission in responses.
                compact_context: Flag requesting immediate chat context compaction.
        
            Returns:
                Value defined by `chat` contract and consumed by downstream callers.
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
        """Detailed synchronous function documentation for `_compact_messages`.
        
        This callable is implemented in `src/document_analyzer_api/application/services/chat_service.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                messages: Input parameter for `_compact_messages`.
        
            Returns:
                Value defined by `_compact_messages` contract and consumed by downstream callers.
        """
        if len(messages) <= 2:
            return messages

        old_messages = messages[:-2]
        recent_messages = messages[-2:]
        summary = " ".join(message.content for message in old_messages)
        compacted = ChatMessage(role=ChatRole.system, content=f"Context summary: {summary[:500]}")
        return [compacted, *recent_messages]


