from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from document_analyzer_api.application.services.health_service import HealthService

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready(request: Request) -> JSONResponse:
    health_service: HealthService = request.app.state.container.health_service
    report = await health_service.readiness()
    code = status.HTTP_200_OK if report.status == "ok" else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=code, content=report.to_dict())


