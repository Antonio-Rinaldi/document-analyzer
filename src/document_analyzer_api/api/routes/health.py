"""Detailed module documentation for `src/document_analyzer_api/api/routes/health.py`.

File role:
- Located in the API routing layer.
- Defines logic and symbols for `health.py` within Document Analyzer V1.

Purpose:
- Implements HTTP endpoint handlers and translates transport payloads into service calls.

Exported symbols overview:
- Classes: none.
- Functions: health, ready.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from document_analyzer_api.application.services.health_service import HealthService

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Detailed asynchronous function documentation for `health`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/health.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `health` contract and consumed by downstream callers.
    """
    return {"status": "ok"}


@router.get("/ready")
async def ready(request: Request) -> JSONResponse:
    """Detailed asynchronous function documentation for `ready`.
    
    This callable is implemented in `src/document_analyzer_api/api/routes/health.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            request: Incoming request object carrying path/query/body/context information.
    
        Returns:
            Value defined by `ready` contract and consumed by downstream callers.
    """
    health_service: HealthService = request.app.state.container.health_service
    report = await health_service.readiness()
    code = status.HTTP_200_OK if report.status == "ok" else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=code, content=report.to_dict())


