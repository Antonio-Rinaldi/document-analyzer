"""Detailed module documentation for `src/document_analyzer_api/main.py`.

File role:
- Located in the project layer.
- Defines logic and symbols for `main.py` within Document Analyzer V1.

Purpose:
- Bootstraps the FastAPI application and wires routers, middleware, and lifecycle hooks.

Exported symbols overview:
- Classes: none.
- Functions: create_app.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

import logging

from fastapi import FastAPI

from .api.errors import register_exception_handlers
from .api.routes.documents import router as documents_router
from .api.routes.health import router as health_router
from .api.routes.metrics import router as metrics_router
from .bootstrap.container import AppContainer
from .config.settings import Settings
from .observability.request_logging import RequestLoggingMiddleware
from .observability.tracing import init_tracing, shutdown_tracing


API_V1_PREFIX = "/api/v1"


def create_app(settings: Settings | None = None) -> FastAPI:
    """Detailed synchronous function documentation for `create_app`.
    
    This callable is implemented in `src/document_analyzer_api/main.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Creates a new resource and returns identifiers or resulting payloads.
    
        Args:
            settings: Typed runtime settings used to configure behavior and integrations.
    
        Returns:
            Value defined by `create_app` contract and consumed by downstream callers.
    """
    logging.basicConfig(level=logging.INFO)
    app_settings = settings or Settings()
    app_settings.validate_runtime()
    init_tracing(app_settings)
    container = AppContainer.from_settings(app_settings)

    app = FastAPI(title="Document Analyzer API", version="0.1.0")
    app.state.container = container
    app.add_middleware(RequestLoggingMiddleware)

    register_exception_handlers(app)
    app.include_router(health_router, prefix=API_V1_PREFIX)
    app.include_router(documents_router, prefix=API_V1_PREFIX)
    app.include_router(metrics_router, prefix=API_V1_PREFIX)
    app.add_event_handler("shutdown", shutdown_tracing)
    return app


app = create_app()



