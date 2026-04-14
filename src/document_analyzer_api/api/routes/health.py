"""Module `src/document_analyzer_api/api/routes/health.py`.

This module belongs to the API routing layer of Document Analyzer.

Purpose:
- Adapts HTTP input/output contracts to application-service calls.

Defined symbols:
- Classes: none.
- Functions: health, ready.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from document_analyzer_api.application.services.health_service import HealthService

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Asynchronous execution path for `health`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/health.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (get) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `dict[str, str]`.
    """
    return {"status": "ok"}


@router.get("/ready")
async def ready(request: Request) -> JSONResponse:
    """Asynchronous execution path for `ready`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/health.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (JSONResponse, get, readiness, to_dict) to satisfy the callable contract.
    
        Args:
            request: Incoming HTTP request carrying route/query/body/context data.
    
        Returns:
            A value compatible with `JSONResponse`.
    """
    health_service: HealthService = request.app.state.container.health_service
    report = await health_service.readiness()
    code = status.HTTP_200_OK if report.status == "ok" else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=code, content=report.to_dict())


