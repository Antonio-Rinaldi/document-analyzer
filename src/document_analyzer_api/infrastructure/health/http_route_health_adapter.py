"""HTTP route readiness adapter for upstream application services."""

from __future__ import annotations

import httpx

from ...domain.ports.health import DependencyStatus


class HttpRouteHealthAdapter:
    """Check an upstream HTTP route using the same base URL used by runtime adapters."""

    def __init__(
        self,
        *,
        name: str,
        base_url: str,
        path: str,
        timeout_seconds: float,
        payload: dict | None = None,
        method: str = "POST",
    ) -> None:
        self._name = name
        self._base_url = base_url.rstrip("/")
        self._path = path
        self._timeout_seconds = timeout_seconds
        self._payload = payload
        self._method = method.upper()

    async def check(self) -> DependencyStatus:
        url = f"{self._base_url}{self._path}"
        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds, trust_env=False) as client:
                if self._method == "GET":
                    response = await client.get(url)
                else:
                    response = await client.post(url, json=self._payload or {})

            if response.status_code == 404:
                return DependencyStatus(name=self._name, ok=False, detail=f"route not found: {self._method} {self._path}")
            if response.status_code >= 500:
                return DependencyStatus(name=self._name, ok=False, detail=f"upstream error: HTTP {response.status_code}")
            return DependencyStatus(name=self._name, ok=True, detail=f"reachable (HTTP {response.status_code})")
        except Exception as exc:
            return DependencyStatus(name=self._name, ok=False, detail=str(exc))





