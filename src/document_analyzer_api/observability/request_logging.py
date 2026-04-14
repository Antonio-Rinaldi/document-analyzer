"""Module `src/document_analyzer_api/observability/request_logging.py`.

This module belongs to the observability layer of Document Analyzer.

Purpose:
- Implements metrics, tracing, and request-level telemetry support.

Defined symbols:
- Classes: RequestLoggingMiddleware.
- Functions: none.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
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
    """RequestLoggingMiddleware component.
    
    This class is defined in `src/document_analyzer_api/observability/request_logging.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, app: ASGIApp) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/observability/request_logging.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (__init__, getLogger, super) to satisfy the callable contract.
        
            Args:
                app: FastAPI application instance used for registration or lifecycle wiring.
        
            Returns:
                A value compatible with `None`.
        """
        super().__init__(app)
        self._logger = logging.getLogger("document_analyzer.request")

    async def dispatch(self, request: Request, call_next):
        """Asynchronous execution path for `dispatch`.
        
        This callable is implemented in `src/document_analyzer_api/observability/request_logging.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (call_next, dumps, get, info) to satisfy the callable contract.
        
            Args:
                request: Incoming HTTP request carrying route/query/body/context data.
                call_next: Input parameter accepted by `dispatch`.
        
            Returns:
                Return value defined by the callable contract.
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

