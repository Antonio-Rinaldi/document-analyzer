"""Detailed module documentation for `src/document_analyzer_api/infrastructure/persistence/mongo_chat_session_repository.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `mongo_chat_session_repository.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: MongoChatSessionRepository.
- Functions: _serialize_session, _deserialize_session.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any

from ...domain.models.chat import ChatMessage, ChatRole, ChatSession
from ...domain.ports.chat_session_repository import ChatSessionRepositoryPort


class MongoChatSessionRepository(ChatSessionRepositoryPort):
    """Detailed class documentation for `MongoChatSessionRepository`.
    
    This repository adapter belongs to `src/document_analyzer_api/infrastructure/persistence/mongo_chat_session_repository.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, uri: str, database: str, collection: str = "chat_sessions") -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chat_session_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                uri: Input parameter for `__init__`.
                database: Input parameter for `__init__`.
                collection: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        from pymongo import MongoClient

        self._client = MongoClient(uri)
        self._collection = self._client[database][collection]
        self._collection.create_index("sessionId", unique=True)
        self._collection.create_index("expiresAt", expireAfterSeconds=0)

    async def create(self, session_id: str, ttl_seconds: int) -> ChatSession:
        """Detailed asynchronous function documentation for `create`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chat_session_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                session_id: Server-side chat session identifier.
                ttl_seconds: Input parameter for `create`.
        
            Returns:
                Value defined by `create` contract and consumed by downstream callers.
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
        """Detailed asynchronous function documentation for `get`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chat_session_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                session_id: Server-side chat session identifier.
        
            Returns:
                Value defined by `get` contract and consumed by downstream callers.
        """
        payload = await asyncio.to_thread(self._collection.find_one, {"sessionId": session_id}, {"_id": 0})
        if payload is None:
            return None
        return _deserialize_session(payload)

    async def upsert(self, session: ChatSession, ttl_seconds: int) -> None:
        """Detailed asynchronous function documentation for `upsert`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chat_session_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                session: Input parameter for `upsert`.
                ttl_seconds: Input parameter for `upsert`.
        
            Returns:
                Value defined by `upsert` contract and consumed by downstream callers.
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
        """Detailed asynchronous function documentation for `delete`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chat_session_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                session_id: Server-side chat session identifier.
        
            Returns:
                Value defined by `delete` contract and consumed by downstream callers.
        """
        result = await asyncio.to_thread(self._collection.delete_one, {"sessionId": session_id})
        return result.deleted_count > 0


def _serialize_session(session: ChatSession) -> dict[str, Any]:
    """Detailed synchronous function documentation for `_serialize_session`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chat_session_repository.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            session: Input parameter for `_serialize_session`.
    
        Returns:
            Value defined by `_serialize_session` contract and consumed by downstream callers.
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
    """Detailed synchronous function documentation for `_deserialize_session`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/mongo_chat_session_repository.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            payload: Input parameter for `_deserialize_session`.
    
        Returns:
            Value defined by `_deserialize_session` contract and consumed by downstream callers.
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

