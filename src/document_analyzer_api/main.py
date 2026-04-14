"""Module `src/document_analyzer_api/main.py`.

This module belongs to the project support layer of Document Analyzer.

Purpose:
- Builds the FastAPI application and wires routers, middleware, and lifecycle hooks.

Defined symbols:
- Classes: none.
- Functions: create_app.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
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
    """Synchronous execution path for `create_app`.
    
    This callable is implemented in `src/document_analyzer_api/main.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Creates a resource and returns identifiers or materialized result payloads.
    
        Args:
            settings: Typed runtime configuration controlling integrations and defaults.
    
        Returns:
            A value compatible with `FastAPI`.
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



