"""Detailed module documentation for `src/document_analyzer_api/bootstrap/dependencies.py`.

File role:
- Located in the bootstrap/composition layer.
- Defines logic and symbols for `dependencies.py` within Document Analyzer V1.

Purpose:
- Supports a focused concern in the Document Analyzer codebase.

Exported symbols overview:
- Classes: none.
- Functions: get_container, get_health_service.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from fastapi import Request

from document_analyzer_api.application.services.health_service import HealthService
from document_analyzer_api.bootstrap.container import AppContainer


def get_container(request: Request) -> AppContainer:
    """Detailed synchronous function documentation for `get_container`.
    
    This callable is implemented in `src/document_analyzer_api/bootstrap/dependencies.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Retrieves data from collaborators and returns a normalized representation.
    
        Args:
            request: Incoming request object carrying path/query/body/context information.
    
        Returns:
            Value defined by `get_container` contract and consumed by downstream callers.
    """
    return request.app.state.container


def get_health_service(container: AppContainer) -> HealthService:
    """Detailed synchronous function documentation for `get_health_service`.
    
    This callable is implemented in `src/document_analyzer_api/bootstrap/dependencies.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Retrieves data from collaborators and returns a normalized representation.
    
        Args:
            container: Input parameter for `get_health_service`.
    
        Returns:
            Value defined by `get_health_service` contract and consumed by downstream callers.
    """
    return container.health_service

