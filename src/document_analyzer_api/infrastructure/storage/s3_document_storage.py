import asyncio
import hashlib
from io import BytesIO


class S3DocumentStorage:
    def __init__(
        self,
        *,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        done_extension: str,
    ) -> None:
        from minio import Minio

        self._bucket = bucket
        self._done_extension = done_extension
        self._client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=False)

    async def object_exists(self, name: str) -> bool:
        return await asyncio.to_thread(self._object_exists_sync, name)

    async def object_hash(self, name: str) -> str:
        return await asyncio.to_thread(self._object_hash_sync, name)

    async def put_object(self, name: str, content: bytes) -> None:
        await asyncio.to_thread(self._put_object_sync, name, content)

    async def has_done_marker(self, name: str) -> bool:
        marker = f"{name}{self._done_extension}"
        return await asyncio.to_thread(self._object_exists_sync, marker)

    async def write_done_marker(self, name: str) -> None:
        marker = f"{name}{self._done_extension}"
        await asyncio.to_thread(self._put_object_sync, marker, b"")

    def _ensure_bucket(self) -> None:
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)

    def _object_exists_sync(self, name: str) -> bool:
        self._ensure_bucket()
        try:
            self._client.stat_object(self._bucket, name)
            return True
        except Exception:
            return False

    def _object_hash_sync(self, name: str) -> str:
        self._ensure_bucket()
        response = self._client.get_object(self._bucket, name)
        try:
            hasher = hashlib.sha256()
            for chunk in response.stream(1024 * 1024):
                hasher.update(chunk)
            return hasher.hexdigest()
        finally:
            response.close()
            response.release_conn()

    def _put_object_sync(self, name: str, content: bytes) -> None:
        self._ensure_bucket()
        data = BytesIO(content)
        self._client.put_object(self._bucket, name, data, length=len(content))

