"""Module `tests/unit/test_settings.py`.

This module belongs to the project support layer of Document Analyzer.

Purpose:
- Implements a focused responsibility in the Document Analyzer codebase.

Defined symbols:
- Classes: none.
- Functions: test_settings_defaults, test_settings_validate_runtime_local_mode_ok, test_settings_validate_runtime_rejects_invalid_adapter_mode, test_settings_validate_runtime_requires_real_mode_values.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

from document_analyzer_api.config.settings import Settings


def test_settings_defaults() -> None:
    """Synchronous execution path for `test_settings_defaults`.
    
    This callable is implemented in `tests/unit/test_settings.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (Settings, startswith) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
    """
    settings = Settings()
    assert settings.mongodb_uri.startswith("mongodb://")
    assert settings.ollama_base_url.startswith("http")
    assert settings.dependency_timeout_seconds > 0


def test_settings_validate_runtime_local_mode_ok() -> None:
    """Synchronous execution path for `test_settings_validate_runtime_local_mode_ok`.
    
    This callable is implemented in `tests/unit/test_settings.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (Settings, validate_runtime) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
    """
    settings = Settings(adapter_mode="local")
    settings.validate_runtime()


def test_settings_validate_runtime_rejects_invalid_adapter_mode() -> None:
    """Synchronous execution path for `test_settings_validate_runtime_rejects_invalid_adapter_mode`.
    
    This callable is implemented in `tests/unit/test_settings.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (Settings, str, validate_runtime) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
    """
    settings = Settings(adapter_mode="invalid")

    try:
        settings.validate_runtime()
    except ValueError as exc:
        assert "ADAPTER_MODE" in str(exc)
        return

    assert False, "Expected ValueError for invalid ADAPTER_MODE"


def test_settings_validate_runtime_requires_real_mode_values() -> None:
    """Synchronous execution path for `test_settings_validate_runtime_requires_real_mode_values`.
    
    This callable is implemented in `tests/unit/test_settings.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (Settings, str, validate_runtime) to satisfy the callable contract.
    
        Args:
            None.
    
        Returns:
            A value compatible with `None`.
    """
    settings = Settings(adapter_mode="real", ollama_text_model="")

    try:
        settings.validate_runtime()
    except ValueError as exc:
        assert "OLLAMA_TEXT_MODEL" in str(exc)
        return

    assert False, "Expected ValueError for missing real-mode setting"


