"""Detailed module documentation for `tests/unit/test_settings.py`.

File role:
- Located in the project layer.
- Defines logic and symbols for `test_settings.py` within Document Analyzer V1.

Purpose:
- Supports a focused concern in the Document Analyzer codebase.

Exported symbols overview:
- Classes: none.
- Functions: test_settings_defaults, test_settings_validate_runtime_local_mode_ok, test_settings_validate_runtime_rejects_invalid_adapter_mode, test_settings_validate_runtime_requires_real_mode_values.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

from document_analyzer_api.config.settings import Settings


def test_settings_defaults() -> None:
    """Detailed synchronous function documentation for `test_settings_defaults`.
    
    This callable is implemented in `tests/unit/test_settings.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `test_settings_defaults` contract and consumed by downstream callers.
    """
    settings = Settings()
    assert settings.mongodb_uri.startswith("mongodb://")
    assert settings.ollama_base_url.startswith("http")
    assert settings.dependency_timeout_seconds > 0


def test_settings_validate_runtime_local_mode_ok() -> None:
    """Detailed synchronous function documentation for `test_settings_validate_runtime_local_mode_ok`.
    
    This callable is implemented in `tests/unit/test_settings.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `test_settings_validate_runtime_local_mode_ok` contract and consumed by downstream callers.
    """
    settings = Settings(adapter_mode="local")
    settings.validate_runtime()


def test_settings_validate_runtime_rejects_invalid_adapter_mode() -> None:
    """Detailed synchronous function documentation for `test_settings_validate_runtime_rejects_invalid_adapter_mode`.
    
    This callable is implemented in `tests/unit/test_settings.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `test_settings_validate_runtime_rejects_invalid_adapter_mode` contract and consumed by downstream callers.
    """
    settings = Settings(adapter_mode="invalid")

    try:
        settings.validate_runtime()
    except ValueError as exc:
        assert "ADAPTER_MODE" in str(exc)
        return

    assert False, "Expected ValueError for invalid ADAPTER_MODE"


def test_settings_validate_runtime_requires_real_mode_values() -> None:
    """Detailed synchronous function documentation for `test_settings_validate_runtime_requires_real_mode_values`.
    
    This callable is implemented in `tests/unit/test_settings.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            None.
    
        Returns:
            Value defined by `test_settings_validate_runtime_requires_real_mode_values` contract and consumed by downstream callers.
    """
    settings = Settings(adapter_mode="real", ollama_text_model="")

    try:
        settings.validate_runtime()
    except ValueError as exc:
        assert "OLLAMA_TEXT_MODEL" in str(exc)
        return

    assert False, "Expected ValueError for missing real-mode setting"


