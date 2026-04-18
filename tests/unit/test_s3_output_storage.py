import asyncio

from document_analyzer_api.infrastructure.storage.s3_output_storage import S3OutputStorage


class _FakeMinio:
    def __init__(self, endpoint: str, access_key: str, secret_key: str, secure: bool) -> None:
        _ = access_key
        _ = secret_key
        _ = secure
        self.endpoint = endpoint
        self.put_calls: list[tuple[str, str, int, str | None]] = []
        self.presign_calls: list[tuple[str, str, object]] = []

    def bucket_exists(self, bucket: str) -> bool:
        _ = bucket
        return True

    def make_bucket(self, bucket: str) -> None:
        _ = bucket

    def put_object(self, bucket: str, filename: str, content_io, length: int, content_type: str | None) -> None:
        _ = content_io
        self.put_calls.append((bucket, filename, length, content_type))

    def presigned_get_object(self, bucket: str, filename: str, expires):
        self.presign_calls.append((bucket, filename, expires))
        return f"http://{self.endpoint}/{bucket}/{filename}?signature=fake"


def test_s3_output_storage_returns_presigned_download_url(monkeypatch) -> None:
    import minio

    fake_holder: dict[str, _FakeMinio] = {}

    def _fake_minio(endpoint: str, access_key: str, secret_key: str, secure: bool):
        client = _FakeMinio(endpoint, access_key, secret_key, secure)
        fake_holder["client"] = client
        return client

    monkeypatch.setattr(minio, "Minio", _fake_minio)

    storage = S3OutputStorage(
        endpoint="localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        bucket="documents-output",
        presign_ttl_seconds=600,
    )

    url = asyncio.run(storage.write_output("summary.md", b"hello", "text/markdown"))

    client = fake_holder["client"]
    assert url.startswith("http://localhost:9000/documents-output/summary.md")
    assert client.put_calls == [("documents-output", "summary.md", 5, "text/markdown")]
    assert len(client.presign_calls) == 1

