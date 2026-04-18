import asyncio

import pytest

from document_analyzer_api.observability import metrics, tracing


def _reset_metrics_state() -> None:
    metrics._REQUEST_TOTAL.clear()
    metrics._REQUEST_DURATION_SUM.clear()
    metrics._REQUEST_DURATION_COUNT.clear()
    metrics._OPERATION_TOTAL.clear()
    metrics._OPERATION_DURATION_SUM.clear()
    metrics._OPERATION_DURATION_COUNT.clear()
    metrics._OPERATION_ERRORS.clear()


def test_metered_async_records_success_metrics() -> None:
    _reset_metrics_state()

    @metrics.metered_async("service.test", "ok")
    async def _op() -> str:
        return "ok"

    result = asyncio.run(_op())

    assert result == "ok"
    assert metrics._OPERATION_TOTAL[("service.test", "ok", "success")] == 1
    assert metrics._OPERATION_DURATION_COUNT[("service.test", "ok")] == 1


def test_metered_sync_records_error_metrics() -> None:
    _reset_metrics_state()

    @metrics.metered_sync("service.test", "boom")
    def _op() -> None:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        _op()

    assert metrics._OPERATION_TOTAL[("service.test", "boom", "error")] == 1
    assert metrics._OPERATION_ERRORS[("service.test", "boom", "RuntimeError")] == 1


def test_traced_sync_handles_attribute_builder_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    observed: list[tuple[str, object]] = []

    monkeypatch.setattr(tracing, "set_span_attribute", lambda key, value: observed.append((key, value)))

    def _bad_attributes() -> dict[str, str]:
        raise ValueError("x")

    @tracing.traced_sync("sync.span", attribute_builder=_bad_attributes)
    def _op() -> int:
        return 7

    assert _op() == 7
    assert ("span.name", "sync.span") in observed


