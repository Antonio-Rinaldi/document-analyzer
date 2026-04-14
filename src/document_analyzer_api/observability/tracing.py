"""Module `src/document_analyzer_api/observability/tracing.py`.

This module belongs to the observability layer of Document Analyzer.

Purpose:
- Initializes trace export and exposes decorator helpers used by tracing wrappers.

Defined symbols:
- Classes: none.
- Functions: init_tracing, shutdown_tracing, start_span, set_span_attribute, traced_async.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from __future__ import annotations

from contextlib import nullcontext
from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar

from ..config.settings import Settings


T = TypeVar("T")
_PROVIDER_INITIALIZED = False


def init_tracing(settings: Settings) -> None:
    """Synchronous execution path for `init_tracing`.
    
    This callable is implemented in `src/document_analyzer_api/observability/tracing.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (BatchSpanProcessor, OTLPSpanExporter, TraceIdRatioBased, TracerProvider) to satisfy the callable contract.
    
        Args:
            settings: Typed runtime configuration controlling integrations and defaults.
    
        Returns:
            A value compatible with `None`.
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
    """Synchronous execution path for `shutdown_tracing`.
    
    This callable is implemented in `src/document_analyzer_api/observability/tracing.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (callable, get_tracer_provider, getattr, shutdown) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
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
    """Synchronous execution path for `start_span`.
    
    This callable is implemented in `src/document_analyzer_api/observability/tracing.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (get_tracer, nullcontext, start_as_current_span) to satisfy the callable contract.
    
        Args:
            name: Identifier/environment key consumed by this callable.
    
        Returns:
            Return value defined by the callable contract.
    """
    try:
        from opentelemetry import trace

        tracer = trace.get_tracer("document_analyzer")
        return tracer.start_as_current_span(name)
    except Exception:
        return nullcontext()


def set_span_attribute(key: str, value: Any) -> None:
    """Synchronous execution path for `set_span_attribute`.
    
    This callable is implemented in `src/document_analyzer_api/observability/tracing.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (get_current_span, set_attribute) to satisfy the callable contract.
    
        Args:
            key: Input parameter accepted by `set_span_attribute`.
            value: Input parameter accepted by `set_span_attribute`.
    
        Returns:
            A value compatible with `None`.
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
    """Synchronous execution path for `traced_async`.
    
    This callable is implemented in `src/document_analyzer_api/observability/tracing.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (attribute_builder, func, items, set_span_attribute) to satisfy the callable contract.
    
        Args:
            span_name: Input parameter accepted by `traced_async`.
            attribute_builder: Input parameter accepted by `traced_async`.
    
        Returns:
            A value compatible with `Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]`.
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        """Synchronous execution path for `decorator`.
        
        This callable is implemented in `src/document_analyzer_api/observability/tracing.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Coordinates helper calls (attribute_builder, func, items, set_span_attribute) to satisfy the callable contract.
        
            Args:
                func: Input parameter accepted by `decorator`.
        
            Returns:
                A value compatible with `Callable[..., Awaitable[T]]`.
        """

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            """Asynchronous execution path for `wrapper`.
            
            This callable is implemented in `src/document_analyzer_api/observability/tracing.py` and contributes to module-level behavior
            with explicit and testable execution semantics.
            
                Behavior:
                    Coordinates helper calls (attribute_builder, func, items, set_span_attribute) to satisfy the callable contract.
            
                Args:
                    *args: Input parameter accepted by `wrapper`.
                    **kwargs: Input parameter accepted by `wrapper`.
            
                Returns:
                    A value compatible with `T`.
            """
            with start_span(span_name):
                if attribute_builder is not None:
                    attributes = attribute_builder(*args, **kwargs)
                    for key, value in attributes.items():
                        set_span_attribute(key, value)
                return await func(*args, **kwargs)

        return wrapper

    return decorator

