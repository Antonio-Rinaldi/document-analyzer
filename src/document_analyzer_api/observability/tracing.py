from __future__ import annotations

from contextlib import nullcontext
from typing import Any


def start_span(name: str):
    try:
        from opentelemetry import trace

        tracer = trace.get_tracer("document_analyzer")
        return tracer.start_as_current_span(name)
    except Exception:
        return nullcontext()


def set_span_attribute(key: str, value: Any) -> None:
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        if span is not None:
            span.set_attribute(key, value)
    except Exception:
        return

