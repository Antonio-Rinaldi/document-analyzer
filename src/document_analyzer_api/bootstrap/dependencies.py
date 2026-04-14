"""Module `src/document_analyzer_api/bootstrap/dependencies.py`.

This module belongs to the composition/bootstrap layer of Document Analyzer.

Purpose:
- Implements a focused responsibility in the Document Analyzer codebase.

Defined symbols:
- Classes: none.
- Functions: get_container, get_health_service.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from fastapi import Request

from document_analyzer_api.application.services.health_service import HealthService
from document_analyzer_api.bootstrap.container import AppContainer


def get_container(request: Request) -> AppContainer:
    """Synchronous execution path for `get_container`.
    
    This callable is implemented in `src/document_analyzer_api/bootstrap/dependencies.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Retrieves data from collaborators and returns a normalized representation.
    
        Args:
            request: Incoming HTTP request carrying route/query/body/context data.
    
        Returns:
            A value compatible with `AppContainer`.
    """
    return request.app.state.container


def get_health_service(container: AppContainer) -> HealthService:
    """Synchronous execution path for `get_health_service`.
    
    This callable is implemented in `src/document_analyzer_api/bootstrap/dependencies.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Retrieves data from collaborators and returns a normalized representation.
    
        Args:
            container: Input parameter accepted by `get_health_service`.
    
        Returns:
            A value compatible with `HealthService`.
    """
    return container.health_service

