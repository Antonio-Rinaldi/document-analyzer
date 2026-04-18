"""Module `tests/unit/test_settings.py`.

This module belongs to the project support layer of Document Analyzer.

Purpose:
- Implements a focused responsibility in the Document Analyzer codebase.

Defined symbols:
- Classes: none.
- Functions: test_settings_defaults, test_settings_validate_runtime_requires_required_values.

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


def test_settings_validate_runtime_requires_required_values() -> None:
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
    settings = Settings(ollama_text_model="")

    try:
        settings.validate_runtime()
    except ValueError as exc:
        assert "OLLAMA_TEXT_MODEL" in str(exc)
        return

    assert False, "Expected ValueError for missing required setting"


def test_settings_validate_runtime_rejects_non_positive_presign_ttl() -> None:
    """Synchronous execution path for `test_settings_validate_runtime_rejects_non_positive_presign_ttl`.

    This callable is implemented in `tests/unit/test_settings.py` and contributes to module-level behavior
    with explicit and testable execution semantics.

        Behavior:
            Verifies startup validation fails when S3 presigned URL TTL is invalid.

        Args:
            None.

        Returns:
            A value compatible with `None`.
    """
    settings = Settings(s3_output_presign_ttl_seconds=0)

    try:
        settings.validate_runtime()
    except ValueError as exc:
        assert "S3_OUTPUT_PRESIGN_TTL_SECONDS" in str(exc)
        return

    assert False, "Expected ValueError for invalid S3_OUTPUT_PRESIGN_TTL_SECONDS"


