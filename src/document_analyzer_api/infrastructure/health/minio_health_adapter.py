from document_analyzer_api.domain.ports.health import DependencyStatus


class MinioHealthAdapter:
    def __init__(self, endpoint: str, access_key: str, secret_key: str, timeout_seconds: float) -> None:
        self._endpoint = endpoint
        self._access_key = access_key
        self._secret_key = secret_key
        self._timeout_seconds = timeout_seconds

    async def check(self) -> DependencyStatus:
        try:
            from minio import Minio

            client = Minio(
                self._endpoint,
                access_key=self._access_key,
                secret_key=self._secret_key,
                secure=False,
            )
            # list_buckets triggers auth and connectivity checks.
            client.list_buckets()
            return DependencyStatus(name="minio", ok=True, detail="reachable")
        except Exception as exc:
            return DependencyStatus(name="minio", ok=False, detail=str(exc))


