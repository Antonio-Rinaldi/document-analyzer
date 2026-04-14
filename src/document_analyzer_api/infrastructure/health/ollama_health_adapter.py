"""Module `src/document_analyzer_api/infrastructure/health/ollama_health_adapter.py`.

This module belongs to the infrastructure adapter layer of Document Analyzer.

Purpose:
- Implements concrete integrations for storage, retrieval, parsing, and providers.

Defined symbols:
- Classes: OllamaHealthAdapter.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import asyncio
import urllib.error
import urllib.request

from document_analyzer_api.domain.ports.health import DependencyStatus


class OllamaHealthAdapter:
    """OllamaHealthAdapter component.
    
    This class is defined in `src/document_analyzer_api/infrastructure/health/ollama_health_adapter.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, base_url: str, timeout_seconds: float) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/health/ollama_health_adapter.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (rstrip) to satisfy the callable contract.
        
            Args:
                base_url: Input parameter accepted by `__init__`.
                timeout_seconds: Input parameter accepted by `__init__`.
        
            Returns:
                A value compatible with `None`.
        """
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    async def check(self) -> DependencyStatus:
        """Asynchronous execution path for `check`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/health/ollama_health_adapter.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (AsyncClient, DependencyStatus, get, raise_for_status) to satisfy the callable contract.
        
            Args:
                None.
        
            Returns:
                A value compatible with `DependencyStatus`.
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
        """Synchronous execution path for `_check_with_urllib`.
        
        This callable is implemented in `src/document_analyzer_api/infrastructure/health/ollama_health_adapter.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (HTTPError, Request, urlopen) to satisfy the callable contract.
        
            Args:
                None.
        
            Returns:
                A value compatible with `None`.
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


