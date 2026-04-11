from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any

from ...domain.models.chat import ChatMessage, ChatRole, ChatSession
from ...domain.ports.chat_session_repository import ChatSessionRepositoryPort


class MongoChatSessionRepository(ChatSessionRepositoryPort):
    def __init__(self, uri: str, database: str, collection: str = "chat_sessions") -> None:
        from pymongo import MongoClient

        self._client = MongoClient(uri)
        self._collection = self._client[database][collection]
        self._collection.create_index("sessionId", unique=True)
        self._collection.create_index("expiresAt", expireAfterSeconds=0)

    async def create(self, session_id: str, ttl_seconds: int) -> ChatSession:
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
        payload = await asyncio.to_thread(self._collection.find_one, {"sessionId": session_id}, {"_id": 0})
        if payload is None:
            return None
        return _deserialize_session(payload)

    async def upsert(self, session: ChatSession, ttl_seconds: int) -> None:
        expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds) if ttl_seconds > 0 else None
        session.expires_at = expires_at
        await asyncio.to_thread(
            self._collection.update_one,
            {"sessionId": session.session_id},
            {"$set": _serialize_session(session)},
            True,
        )

    async def delete(self, session_id: str) -> bool:
        result = await asyncio.to_thread(self._collection.delete_one, {"sessionId": session_id})
        return result.deleted_count > 0


def _serialize_session(session: ChatSession) -> dict[str, Any]:
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

