"""Detailed module documentation for `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `local_chat_session_repository.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: LocalChatSessionRepository.
- Functions: _serialize_session, _deserialize_session, _parse_datetime.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

import asyncio
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from ...domain.models.chat import ChatMessage, ChatRole, ChatSession
from ...domain.ports.chat_session_repository import ChatSessionRepositoryPort


class LocalChatSessionRepository(ChatSessionRepositoryPort):
    """Detailed class documentation for `LocalChatSessionRepository`.
    
    This repository adapter belongs to `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, root_path: str) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                root_path: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._file_path = Path(root_path) / "chat_sessions.json"

    async def create(self, session_id: str, ttl_seconds: int) -> ChatSession:
        """Detailed asynchronous function documentation for `create`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to the module workflow
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

        records = await self._load_records()
        records = [item for item in records if item.get("sessionId") != session_id]
        records.append(_serialize_session(session))
        await self._save_records(records)
        return session

    async def get(self, session_id: str) -> ChatSession | None:
        """Detailed asynchronous function documentation for `get`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                session_id: Server-side chat session identifier.
        
            Returns:
                Value defined by `get` contract and consumed by downstream callers.
        """
        records = await self._load_records()
        now = datetime.now(UTC)
        changed = False

        active: list[dict[str, Any]] = []
        found: ChatSession | None = None
        for item in records:
            expires_at = _parse_datetime(item.get("expiresAt"))
            if expires_at is not None and expires_at <= now:
                changed = True
                continue
            active.append(item)
            if item.get("sessionId") == session_id:
                found = _deserialize_session(item)

        if changed:
            await self._save_records(active)

        return found

    async def upsert(self, session: ChatSession, ttl_seconds: int) -> None:
        """Detailed asynchronous function documentation for `upsert`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                session: Input parameter for `upsert`.
                ttl_seconds: Input parameter for `upsert`.
        
            Returns:
                Value defined by `upsert` contract and consumed by downstream callers.
        """
        records = await self._load_records()
        expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds) if ttl_seconds > 0 else None
        session.expires_at = expires_at

        updated = False
        payload = _serialize_session(session)
        for idx, item in enumerate(records):
            if item.get("sessionId") == session.session_id:
                records[idx] = payload
                updated = True
                break

        if not updated:
            records.append(payload)

        await self._save_records(records)

    async def delete(self, session_id: str) -> bool:
        """Detailed asynchronous function documentation for `delete`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                session_id: Server-side chat session identifier.
        
            Returns:
                Value defined by `delete` contract and consumed by downstream callers.
        """
        records = await self._load_records()
        filtered = [item for item in records if item.get("sessionId") != session_id]
        removed = len(filtered) != len(records)
        if removed:
            await self._save_records(filtered)
        return removed

    async def _load_records(self) -> list[dict[str, Any]]:
        """Detailed asynchronous function documentation for `_load_records`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `_load_records` contract and consumed by downstream callers.
        """
        def _read() -> list[dict[str, Any]]:
            """Detailed synchronous function documentation for `_read`.
            
            This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to the module workflow
            through deterministic input/output behavior and explicit collaboration contracts.
            
                Behavior:
                    Executes the callable contract for this module responsibility.
            
                Args:
                    None.
            
                Returns:
                    Value defined by `_read` contract and consumed by downstream callers.
            """
            if not self._file_path.exists():
                return []
            return json.loads(self._file_path.read_text(encoding="utf-8"))

        return await asyncio.to_thread(_read)

    async def _save_records(self, records: list[dict[str, Any]]) -> None:
        """Detailed asynchronous function documentation for `_save_records`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                records: Input parameter for `_save_records`.
        
            Returns:
                Value defined by `_save_records` contract and consumed by downstream callers.
        """
        def _write() -> None:
            """Detailed synchronous function documentation for `_write`.
            
            This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to the module workflow
            through deterministic input/output behavior and explicit collaboration contracts.
            
                Behavior:
                    Executes the callable contract for this module responsibility.
            
                Args:
                    None.
            
                Returns:
                    Value defined by `_write` contract and consumed by downstream callers.
            """
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            self._file_path.write_text(json.dumps(records), encoding="utf-8")

        await asyncio.to_thread(_write)


def _serialize_session(session: ChatSession) -> dict[str, Any]:
    """Detailed synchronous function documentation for `_serialize_session`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to the module workflow
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
        "expiresAt": session.expires_at.isoformat() if session.expires_at else None,
        "messages": [
            {
                "role": message.role.value,
                "content": message.content,
                "createdAt": message.created_at.isoformat(),
            }
            for message in session.messages
        ],
    }


def _deserialize_session(payload: dict[str, Any]) -> ChatSession:
    """Detailed synchronous function documentation for `_deserialize_session`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to the module workflow
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
            created_at=_parse_datetime(item.get("createdAt")) or datetime.now(UTC),
        )
        for item in payload.get("messages", [])
    ]

    return ChatSession(
        session_id=payload["sessionId"],
        messages=messages,
        expires_at=_parse_datetime(payload.get("expiresAt")),
    )


def _parse_datetime(value: Any) -> datetime | None:
    """Detailed synchronous function documentation for `_parse_datetime`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            value: Input parameter for `_parse_datetime`.
    
        Returns:
            Value defined by `_parse_datetime` contract and consumed by downstream callers.
    """
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)

