"""Detailed module documentation for `src/document_analyzer_api/observability/request_logging.py`.

File role:
- Located in the observability layer.
- Defines logic and symbols for `request_logging.py` within Document Analyzer V1.

Purpose:
- Supports a focused concern in the Document Analyzer codebase.

Exported symbols overview:
- Classes: RequestLoggingMiddleware.
- Functions: none.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from __future__ import annotations

import json
import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .metrics import observe_request


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Detailed class documentation for `RequestLoggingMiddleware`.
    
    This component belongs to `src/document_analyzer_api/observability/request_logging.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    def __init__(self, app: ASGIApp) -> None:
        """Detailed synchronous function documentation for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/observability/request_logging.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                app: FastAPI application instance used for registration or runtime access.
        
            Returns:
                Value defined by `__init__` contract and consumed by downstream callers.
        """
        super().__init__(app)
        self._logger = logging.getLogger("document_analyzer.request")

    async def dispatch(self, request: Request, call_next):
        """Detailed asynchronous function documentation for `dispatch`.
        
        This callable is implemented in `src/document_analyzer_api/observability/request_logging.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                request: Incoming request object carrying path/query/body/context information.
                call_next: Input parameter for `dispatch`.
        
            Returns:
                Value defined by `dispatch` contract and consumed by downstream callers.
        """
        request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex)
        start = time.perf_counter()

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000.0
        observe_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        response.headers["X-Request-ID"] = request_id
        payload = {
            "request_id": request_id,
            "operation": f"{request.method} {request.url.path}",
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 3),
        }
        self._logger.info(json.dumps(payload))
        return response

