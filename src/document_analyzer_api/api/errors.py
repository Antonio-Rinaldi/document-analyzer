"""Module `src/document_analyzer_api/api/errors.py`.

This module belongs to the API error mapping layer of Document Analyzer.

Purpose:
- Maps internal failures to RFC 7807 problem responses returned by the HTTP API.

Defined symbols:
- Classes: DomainError, ValidationProblem.
- Functions: register_exception_handlers.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .schemas.problem import ProblemDetails


class DomainError(Exception):
    """DomainError error model.
    
    This class is defined in `src/document_analyzer_api/api/errors.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(
        self,
        *,
        status: int,
        title: str,
        detail: str,
        error_code: str,
        problem_type: str = "urn:problem:domain-error",
        details: dict | list | None = None,
    ) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/api/errors.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (__init__, super) to satisfy the callable contract.
        
            Args:
                status: Status value/code used for downstream branching and response mapping.
                title: Input parameter accepted by `__init__`.
                detail: Human-readable detail text (often for problem/error payloads).
                error_code: Stable machine-readable code for client-side error handling.
                problem_type: Problem type identifier following RFC 7807 semantics.
                details: Optional structured metadata attached to operation or error outcomes.
        
            Returns:
                A value compatible with `None`.
        """
        super().__init__(detail)
        self.status = status
        self.title = title
        self.detail = detail
        self.error_code = error_code
        self.problem_type = problem_type
        self.details = details


class ValidationProblem(DomainError):
    """ValidationProblem component.
    
    This class is defined in `src/document_analyzer_api/api/errors.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: no explicit annotated fields.
    """
    def __init__(self, detail: str, details: dict | list | None = None) -> None:
        """Synchronous execution path for `__init__`.
        
        This callable is implemented in `src/document_analyzer_api/api/errors.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (__init__, super) to satisfy the callable contract.
        
            Args:
                detail: Human-readable detail text (often for problem/error payloads).
                details: Optional structured metadata attached to operation or error outcomes.
        
            Returns:
                A value compatible with `None`.
        """
        super().__init__(
            status=400,
            title="Bad Request",
            detail=detail,
            error_code="VALIDATION_ERROR",
            problem_type="urn:problem:validation-error",
            details=details,
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Synchronous execution path for `register_exception_handlers`.
    
    This callable is implemented in `src/document_analyzer_api/api/errors.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (JSONResponse, ProblemDetails, errors, exception_handler) to satisfy the callable contract.
    
        Args:
            app: FastAPI application instance used for registration or lifecycle wiring.
    
        Returns:
            A value compatible with `None`.
    """

    @app.exception_handler(DomainError)
    async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
        """Asynchronous execution path for `domain_error_handler`.
        
        This callable is implemented in `src/document_analyzer_api/api/errors.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (JSONResponse, ProblemDetails, exception_handler, model_dump) to satisfy the callable contract.
        
            Args:
                _: Input parameter accepted by `domain_error_handler`.
                exc: Exception instance being mapped, wrapped, or inspected.
        
            Returns:
                A value compatible with `JSONResponse`.
        """
        body = ProblemDetails(
            type=exc.problem_type,
            title=exc.title,
            status=exc.status,
            detail=exc.detail,
            errorCode=exc.error_code,
            details=exc.details,
        )
        return JSONResponse(
            status_code=exc.status,
            content=body.model_dump(exclude_none=True),
            media_type="application/problem+json",
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Asynchronous execution path for `request_validation_handler`.
        
        This callable is implemented in `src/document_analyzer_api/api/errors.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (JSONResponse, ProblemDetails, errors, exception_handler) to satisfy the callable contract.
        
            Args:
                request: Incoming HTTP request carrying route/query/body/context data.
                exc: Exception instance being mapped, wrapped, or inspected.
        
            Returns:
                A value compatible with `JSONResponse`.
        """
        body = ProblemDetails(
            type="urn:problem:request-validation",
            title="Bad Request",
            status=400,
            detail="Request validation failed",
            instance=str(request.url.path),
            errorCode="REQUEST_VALIDATION_ERROR",
            details=exc.errors(),
        )
        return JSONResponse(
            status_code=400,
            content=body.model_dump(exclude_none=True),
            media_type="application/problem+json",
        )


