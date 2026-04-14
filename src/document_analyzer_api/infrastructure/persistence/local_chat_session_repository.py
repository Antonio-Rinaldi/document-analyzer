"""Module `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: LocalChatSessionRepository.
- Functions: _serialize_session, _deserialize_session, _parse_datetime.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import asyncio
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from ...domain.models.chat import ChatMessage, ChatRole, ChatSession
from ...domain.ports.chat_session_repository import ChatSessionRepositoryPort


class LocalChatSessionRepository(ChatSessionRepositoryPort):
    """LocalChatSessionRepository repository adapter.
    
    This class is defined in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, root_path: str) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (Path) to satisfy the callable contract.
        
            Args:
                root_path: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._file_path = Path(root_path) / "chat_sessions.json"

    async def create(self, session_id: str, ttl_seconds: int) -> ChatSession:
        """Asynchronous execution path for `create`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (ChatSession, _load_records, _save_records, _serialize_session) to satisfy the callable contract.
        
            Args:
                session_id: Server-side chat session identifier.
                ttl_seconds: Input parameter accepted by `create`.
        
            Returns:
                A value compatible with `ChatSession`.
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
        """Asynchronous execution path for `get`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (_deserialize_session, _load_records, _parse_datetime, _save_records) to satisfy the callable contract.
        
            Args:
                session_id: Server-side chat session identifier.
        
            Returns:
                A value compatible with `ChatSession | None`.
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
        """Asynchronous execution path for `upsert`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (_load_records, _save_records, _serialize_session, append) to satisfy the callable contract.
        
            Args:
                session: Input parameter accepted by `upsert`.
                ttl_seconds: Input parameter accepted by `upsert`.
        
            Returns:
                A value compatible with `None`.
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
        """Asynchronous execution path for `delete`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (_load_records, _save_records, get, len) to satisfy the callable contract.
        
            Args:
                session_id: Server-side chat session identifier.
        
            Returns:
                A value compatible with `bool`.
        """
        records = await self._load_records()
        filtered = [item for item in records if item.get("sessionId") != session_id]
        removed = len(filtered) != len(records)
        if removed:
            await self._save_records(filtered)
        return removed

    async def _load_records(self) -> list[dict[str, Any]]:
        """Asynchronous execution path for `_load_records`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (exists, loads, read_text, to_thread) to satisfy the callable contract.
        
            Args:
                None.
        
            Returns:
                A value compatible with `list[dict[str, Any]]`.
        """
        def _read() -> list[dict[str, Any]]:
            """Synchronous execution path for `_read`.
            
            This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to module-level behavior
            with explicit and testable execution semantics.
            
                Behavior:
                    Coordinates helper calls (exists, loads, read_text) to satisfy the callable contract.
            
                Args:
                    None.
            
                Returns:
                    A value compatible with `list[dict[str, Any]]`.
            """
            if not self._file_path.exists():
                return []
            return json.loads(self._file_path.read_text(encoding="utf-8"))

        return await asyncio.to_thread(_read)

    async def _save_records(self, records: list[dict[str, Any]]) -> None:
        """Asynchronous execution path for `_save_records`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (dumps, mkdir, to_thread, write_text) to satisfy the callable contract.
        
            Args:
                records: Input parameter accepted by `_save_records`.
        
            Returns:
                A value compatible with `None`.
        """
        def _write() -> None:
            """Synchronous execution path for `_write`.
            
            This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to module-level behavior
            with explicit and testable execution semantics.
            
                Behavior:
                    Coordinates helper calls (dumps, mkdir, write_text) to satisfy the callable contract.
            
                Args:
                    None.
            
                Returns:
                    A value compatible with `None`.
            """
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            self._file_path.write_text(json.dumps(records), encoding="utf-8")

        await asyncio.to_thread(_write)


def _serialize_session(session: ChatSession) -> dict[str, Any]:
    """Synchronous execution path for `_serialize_session`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (isoformat) to satisfy the callable contract.
    
        Args:
            session: Input parameter accepted by `_serialize_session`.
    
        Returns:
            A value compatible with `dict[str, Any]`.
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
    """Synchronous execution path for `_deserialize_session`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (ChatMessage, ChatRole, ChatSession, _parse_datetime) to satisfy the callable contract.
    
        Args:
            payload: Input parameter accepted by `_deserialize_session`.
    
        Returns:
            A value compatible with `ChatSession`.
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
    """Synchronous execution path for `_parse_datetime`.
    
    This callable is implemented in `src/document_analyzer_api/infrastructure/persistence/local_chat_session_repository.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (fromisoformat, isinstance) to satisfy the callable contract.
    
        Args:
            value: Input parameter accepted by `_parse_datetime`.
    
        Returns:
            A value compatible with `datetime | None`.
    """
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)

