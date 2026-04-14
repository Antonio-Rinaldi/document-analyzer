"""Detailed module documentation for `src/document_analyzer_api/observability/tracing.py`.

File role:
- Located in the observability layer.
- Defines logic and symbols for `tracing.py` within Document Analyzer V1.

Purpose:
- Provides tracing initialization and decorator utilities for wrapper-based instrumentation.

Exported symbols overview:
- Classes: none.
- Functions: init_tracing, shutdown_tracing, start_span, set_span_attribute, traced_async.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from __future__ import annotations

from contextlib import nullcontext
from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar

from ..config.settings import Settings


T = TypeVar("T")
_PROVIDER_INITIALIZED = False


def init_tracing(settings: Settings) -> None:
    """Detailed synchronous function documentation for `init_tracing`.
    
    This callable is implemented in `src/document_analyzer_api/observability/tracing.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            settings: Typed runtime settings used to configure behavior and integrations.
    
        Returns:
            Value defined by `init_tracing` contract and consumed by downstream callers.
    """
    global _PROVIDER_INITIALIZED
    if _PROVIDER_INITIALIZED or not settings.tracing_enabled:
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

        provider = TracerProvider(
            resource=Resource.create({"service.name": settings.tracing_service_name}),
            sampler=TraceIdRatioBased(settings.tracing_sample_ratio),
        )
        exporter = OTLPSpanExporter(endpoint=settings.tracing_otlp_endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        _PROVIDER_INITIALIZED = True
    except Exception:
        _PROVIDER_INITIALIZED = False


def shutdown_tracing() -> None:
    """Detailed synchronous function documentation for `shutdown_tracing`.
    
    This callable is implemented in `src/document_analyzer_api/observability/tracing.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `shutdown_tracing` contract and consumed by downstream callers.
    """
    if not _PROVIDER_INITIALIZED:
        return

    try:
        from opentelemetry import trace

        provider = trace.get_tracer_provider()
        shutdown = getattr(provider, "shutdown", None)
        if callable(shutdown):
            shutdown()
    except Exception:
        return


def start_span(name: str):
    """Detailed synchronous function documentation for `start_span`.
    
    This callable is implemented in `src/document_analyzer_api/observability/tracing.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            name: Environment variable or entity name, depending on callable context.
    
        Returns:
            Value defined by `start_span` contract and consumed by downstream callers.
    """
    try:
        from opentelemetry import trace

        tracer = trace.get_tracer("document_analyzer")
        return tracer.start_as_current_span(name)
    except Exception:
        return nullcontext()


def set_span_attribute(key: str, value: Any) -> None:
    """Detailed synchronous function documentation for `set_span_attribute`.
    
    This callable is implemented in `src/document_analyzer_api/observability/tracing.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            key: Input parameter for `set_span_attribute`.
            value: Input parameter for `set_span_attribute`.
    
        Returns:
            Value defined by `set_span_attribute` contract and consumed by downstream callers.
    """
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        if span is not None:
            span.set_attribute(key, value)
    except Exception:
        return


def traced_async(
    span_name: str,
    *,
    attribute_builder: Callable[..., dict[str, Any]] | None = None,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Detailed synchronous function documentation for `traced_async`.
    
    This callable is implemented in `src/document_analyzer_api/observability/tracing.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            span_name: Input parameter for `traced_async`.
            attribute_builder: Input parameter for `traced_async`.
    
        Returns:
            Value defined by `traced_async` contract and consumed by downstream callers.
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        """Detailed synchronous function documentation for `decorator`.
        
        This callable is implemented in `src/document_analyzer_api/observability/tracing.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                func: Input parameter for `decorator`.
        
            Returns:
                Value defined by `decorator` contract and consumed by downstream callers.
        """

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            """Detailed asynchronous function documentation for `wrapper`.
            
            This callable is implemented in `src/document_analyzer_api/observability/tracing.py` and contributes to the module workflow
            through deterministic input/output behavior and explicit collaboration contracts.
            
                Behavior:
                    Executes the callable contract for this module responsibility.
            
                Args:
                    *args: Input parameter for `wrapper`.
                    **kwargs: Input parameter for `wrapper`.
            
                Returns:
                    Value defined by `wrapper` contract and consumed by downstream callers.
            """
            with start_span(span_name):
                if attribute_builder is not None:
                    attributes = attribute_builder(*args, **kwargs)
                    for key, value in attributes.items():
                        set_span_attribute(key, value)
                return await func(*args, **kwargs)

        return wrapper

    return decorator

