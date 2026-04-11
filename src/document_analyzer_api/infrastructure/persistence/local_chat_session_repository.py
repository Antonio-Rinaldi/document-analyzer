import asyncio
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from ...domain.models.chat import ChatMessage, ChatRole, ChatSession
from ...domain.ports.chat_session_repository import ChatSessionRepositoryPort


class LocalChatSessionRepository(ChatSessionRepositoryPort):
    def __init__(self, root_path: str) -> None:
        self._file_path = Path(root_path) / "chat_sessions.json"

    async def create(self, session_id: str, ttl_seconds: int) -> ChatSession:
        now = datetime.now(UTC)
        expires_at = now + timedelta(seconds=ttl_seconds) if ttl_seconds > 0 else None
        session = ChatSession(session_id=session_id, messages=[], expires_at=expires_at)

        records = await self._load_records()
        records = [item for item in records if item.get("sessionId") != session_id]
        records.append(_serialize_session(session))
        await self._save_records(records)
        return session

    async def get(self, session_id: str) -> ChatSession | None:
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
        records = await self._load_records()
        filtered = [item for item in records if item.get("sessionId") != session_id]
        removed = len(filtered) != len(records)
        if removed:
            await self._save_records(filtered)
        return removed

    async def _load_records(self) -> list[dict[str, Any]]:
        def _read() -> list[dict[str, Any]]:
            if not self._file_path.exists():
                return []
            return json.loads(self._file_path.read_text(encoding="utf-8"))

        return await asyncio.to_thread(_read)

    async def _save_records(self, records: list[dict[str, Any]]) -> None:
        def _write() -> None:
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            self._file_path.write_text(json.dumps(records), encoding="utf-8")

        await asyncio.to_thread(_write)


def _serialize_session(session: ChatSession) -> dict[str, Any]:
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
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)

