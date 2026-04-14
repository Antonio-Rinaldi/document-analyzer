"""Detailed module documentation for `src/document_analyzer_api/infrastructure/health/ollama_health_adapter.py`.

File role:
- Located in the infrastructure adapter layer.
- Defines logic and symbols for `ollama_health_adapter.py` within Document Analyzer V1.

Purpose:
- Implements concrete adapters for persistence, providers, parsing, and retrieval backends.

Exported symbols overview:
- Classes: OllamaHealthAdapter.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

import asyncio
import urllib.error
import urllib.request

from document_analyzer_api.domain.ports.health import DependencyStatus


class OllamaHealthAdapter:
    """Detailed class documentation for `OllamaHealthAdapter`.
    
    This component belongs to `src/document_analyzer_api/infrastructure/health/ollama_health_adapter.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, base_url: str, timeout_seconds: float) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/health/ollama_health_adapter.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                base_url: Input parameter for `__init__`.
                timeout_seconds: Input parameter for `__init__`.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    async def check(self) -> DependencyStatus:
        """Detailed asynchronous function documentation for `check`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/health/ollama_health_adapter.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `check` contract and consumed by downstream callers.
        """
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
        """Detailed synchronous function documentation for `_check_with_urllib`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/health/ollama_health_adapter.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `_check_with_urllib` contract and consumed by downstream callers.
        """
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


