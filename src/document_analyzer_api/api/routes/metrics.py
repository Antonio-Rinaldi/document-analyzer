"""Module `src/document_analyzer_api/api/routes/metrics.py`.

This module belongs to the API routing layer of Document Analyzer.

Purpose:
- Adapts HTTP input/output contracts to application-service calls.

Defined symbols:
- Classes: none.
- Functions: metrics.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from ...observability.metrics import render_prometheus_metrics

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
async def metrics() -> PlainTextResponse:
    """Asynchronous execution path for `metrics`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/metrics.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (PlainTextResponse, get, render_prometheus_metrics) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `PlainTextResponse`.
    """
    return PlainTextResponse(render_prometheus_metrics(), media_type="text/plain; version=0.0.4")

