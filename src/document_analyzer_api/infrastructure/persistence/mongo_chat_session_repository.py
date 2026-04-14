"""Module `src/document_analyzer_api/infrastructure/persistence/mongo_chat_session_repository.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: MongoChatSessionRepository.
- Functions: _serialize_session, _deserialize_session.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any

from ...domain.models.chat import ChatMessage, ChatRole, ChatSession
from ...domain.ports.chat_session_repository import ChatSessionRepositoryPort


class MongoChatSessionRepository(ChatSessionRepositoryPort):
    """MongoChatSessionRepository repository adapter.
    
    This class is defined in `src/document_analyzer_api/infrastructure/persistence/mongo_chat_session_repository.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, uri: str, database: str, collection: str = "chat_sessions") -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chat_session_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (MongoClient, create_index) to satisfy the callable contract.
        
            Args:
                uri: Input parameter accepted by `__init__`.
                database: Input parameter accepted by `__init__`.
                collection: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        from pymongo import MongoClient

        self._client = MongoClient(uri)
        self._collection = self._client[database][collection]
        self._collection.create_index("sessionId", unique=True)
        self._collection.create_index("expiresAt", expireAfterSeconds=0)

    async def create(self, session_id: str, ttl_seconds: int) -> ChatSession:
        """Asynchronous execution path for `create`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chat_session_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (ChatSession, _serialize_session, now, timedelta) to satisfy the callable contract.
        
            Args:
                session_id: Server-side chat session identifier.
                ttl_seconds: Input parameter accepted by `create`.
        
            Returns:
                A value compatible with `ChatSession`.
        """
        now = datetime.now(UTC)
        expires_at = now + timedelta(seconds=ttl_seconds) if ttl_seconds > 0 else None
        session = ChatSession(session_id=session_id, messages=[], expires_at=expires_at)

        await asyncio.to_thread(
            self._collection.update_one,
            {"sessionId": session_id},
            {"$set": _serialize_session(session)},
            True,
        )
        return session

    async def get(self, session_id: str) -> ChatSession | None:
        """Asynchronous execution path for `get`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chat_session_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (_deserialize_session, to_thread) to satisfy the callable contract.
        
            Args:
                session_id: Server-side chat session identifier.
        
            Returns:
                A value compatible with `ChatSession | None`.
        """
        payload = await asyncio.to_thread(self._collection.find_one, {"sessionId": session_id}, {"_id": 0})
        if payload is None:
            return None
        return _deserialize_session(payload)

    async def upsert(self, session: ChatSession, ttl_seconds: int) -> None:
        """Asynchronous execution path for `upsert`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chat_session_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (_serialize_session, now, timedelta, to_thread) to satisfy the callable contract.
        
            Args:
                session: Input parameter accepted by `upsert`.
                ttl_seconds: Input parameter accepted by `upsert`.
        
            Returns:
                A value compatible with `None`.
        """
        expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds) if ttl_seconds > 0 else None
        session.expires_at = expires_at
        await asyncio.to_thread(
            self._collection.update_one,
            {"sessionId": session.session_id},
            {"$set": _serialize_session(session)},
            True,
        )

    async def delete(self, session_id: str) -> bool:
        """Asynchronous execution path for `delete`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chat_session_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (to_thread) to satisfy the callable contract.
        
            Args:
                session_id: Server-side chat session identifier.
        
            Returns:
                A value compatible with `bool`.
        """
        result = await asyncio.to_thread(self._collection.delete_one, {"sessionId": session_id})
        return result.deleted_count > 0


def _serialize_session(session: ChatSession) -> dict[str, Any]:
    """Synchronous execution path for `_serialize_session`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chat_session_repository.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Executes the callable contract for this module concern.
    
        Args:
            session: Input parameter accepted by `_serialize_session`.
    
        Returns:
            A value compatible with `dict[str, Any]`.
    """
    return {
        "sessionId": session.session_id,
        "expiresAt": session.expires_at,
        "messages": [
            {
                "role": message.role.value,
                "content": message.content,
                "createdAt": message.created_at,
            }
            for message in session.messages
        ],
    }


def _deserialize_session(payload: dict[str, Any]) -> ChatSession:
    """Synchronous execution path for `_deserialize_session`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chat_session_repository.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (ChatMessage, ChatRole, ChatSession, get) to satisfy the callable contract.
    
        Args:
            payload: Input parameter accepted by `_deserialize_session`.
    
        Returns:
            A value compatible with `ChatSession`.
    """
    messages = [
        ChatMessage(
            role=ChatRole(item["role"]),
            content=item["content"],
            created_at=item.get("createdAt", datetime.now(UTC)),
        )
        for item in payload.get("messages", [])
    ]

    return ChatSession(
        session_id=payload["sessionId"],
        messages=messages,
        expires_at=payload.get("expiresAt"),
    )

