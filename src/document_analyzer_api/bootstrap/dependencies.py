from fastapi import Request

from document_analyzer_api.application.services.health_service import HealthService
from document_analyzer_api.bootstrap.container import AppContainer


def get_container(request: Request) -> AppContainer:
    return request.app.state.container


def get_health_service(container: AppContainer) -> HealthService:
    return container.health_service

