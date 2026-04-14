"""Detailed module documentation for `src/document_analyzer_api/api/routes/metrics.py`.

File role:
- Located in the API routing layer.
- Defines logic and symbols for `metrics.py` within Document Analyzer V1.

Purpose:
- Implements HTTP endpoint handlers and translates transport payloads into service calls.

Exported symbols overview:
- Classes: none.
- Functions: metrics.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from ...observability.metrics import render_prometheus_metrics

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
async def metrics() -> PlainTextResponse:
    """Detailed asynchronous function documentation for `metrics`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/metrics.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `metrics` contract and consumed by downstream callers.
    """
    return PlainTextResponse(render_prometheus_metrics(), media_type="text/plain; version=0.0.4")

