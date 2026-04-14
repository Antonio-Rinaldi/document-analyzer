import asyncio
from io import BytesIO


class S3OutputStorage:
    def __init__(
        self,
        *,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
    ) -> None:
        from minio import Minio

        self._bucket = bucket
        self._client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=False)

    async def write_output(self, filename: str, content: bytes, content_type: str | None = None) -> str:
        await asyncio.to_thread(self._write_sync, filename, content, content_type)
        return f"s3://{self._bucket}/{filename}"

    def _ensure_bucket(self) -> None:
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)

    def _write_sync(self, filename: str, content: bytes, content_type: str | None) -> None:
        self._ensure_bucket()
        self._client.put_object(
            self._bucket,
            filename,
            BytesIO(content),
            length=len(content),
            content_type=content_type,
        )

