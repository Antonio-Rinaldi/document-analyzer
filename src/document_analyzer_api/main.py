import logging

from fastapi import FastAPI

from .api.errors import register_exception_handlers
from .api.routes.documents import router as documents_router
from .api.routes.health import router as health_router
from .api.routes.metrics import router as metrics_router
from .bootstrap.container import AppContainer
from .config.settings import Settings
from .observability.request_logging import RequestLoggingMiddleware


API_V1_PREFIX = "/api/v1"


def create_app(settings: Settings | None = None) -> FastAPI:
    logging.basicConfig(level=logging.INFO)
    app_settings = settings or Settings()
    app_settings.validate_runtime()
    container = AppContainer.from_settings(app_settings)

    app = FastAPI(title="Document Analyzer API", version="0.1.0")
    app.state.container = container
    app.add_middleware(RequestLoggingMiddleware)

    register_exception_handlers(app)
    app.include_router(health_router, prefix=API_V1_PREFIX)
    app.include_router(documents_router, prefix=API_V1_PREFIX)
    app.include_router(metrics_router, prefix=API_V1_PREFIX)
    return app


app = create_app()



