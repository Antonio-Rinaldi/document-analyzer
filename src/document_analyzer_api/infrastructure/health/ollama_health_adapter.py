import asyncio
import urllib.error
import urllib.request

from document_analyzer_api.domain.ports.health import DependencyStatus


class OllamaHealthAdapter:
    def __init__(self, base_url: str, timeout_seconds: float) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    async def check(self) -> DependencyStatus:
        try:
            try:
                import httpx

                async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                    response = await client.get(f"{self._base_url}/api/tags")
                    response.raise_for_status()
            except ModuleNotFoundError:
                await asyncio.to_thread(self._check_with_urllib)
            return DependencyStatus(name="ollama", ok=True, detail="reachable")
        except Exception as exc:
            return DependencyStatus(name="ollama", ok=False, detail=str(exc))

    def _check_with_urllib(self) -> None:
        request = urllib.request.Request(f"{self._base_url}/api/tags", method="GET")
        with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
            if response.status >= 400:
                raise urllib.error.HTTPError(
                    request.full_url,
                    response.status,
                    "ollama health check failed",
                    hdrs=response.headers,
                    fp=None,
                )


