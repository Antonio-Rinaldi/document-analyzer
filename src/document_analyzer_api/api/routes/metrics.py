from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from ...observability.metrics import render_prometheus_metrics

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
async def metrics() -> PlainTextResponse:
    return PlainTextResponse(render_prometheus_metrics(), media_type="text/plain; version=0.0.4")

