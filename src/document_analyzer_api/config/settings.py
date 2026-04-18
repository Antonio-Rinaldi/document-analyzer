"""Module `src/document_analyzer_api/config/settings.py`.

This module belongs to the project support layer of Document Analyzer.

Purpose:
- Defines typed runtime settings loaded from environment variables and validated at startup.

Defined symbols:
- Classes: Settings.
- Functions: _env_int, _env_float, _env_bool.

Project alignment:
- Functional expectations are described in `documentation/REFINED_SPECS.md`.
- Architectural and style conventions are defined in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
"""

import os
from dataclasses import dataclass, field


def _env_int(name: str, default: int) -> int:
    """Synchronous execution path for `_env_int`.
    
    This callable is implemented in `src/document_analyzer_api/config/settings.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (getenv, int) to satisfy the callable contract.
    
        Args:
            name: Identifier/environment key consumed by this callable.
            default: Fallback value used when primary input is absent.
    
        Returns:
            A value compatible with `int`.
    """
    raw = os.getenv(name)
    if raw is None:
        return default
    return int(raw)


def _env_float(name: str, default: float) -> float:
    """Synchronous execution path for `_env_float`.
    
    This callable is implemented in `src/document_analyzer_api/config/settings.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (float, getenv) to satisfy the callable contract.
    
        Args:
            name: Identifier/environment key consumed by this callable.
            default: Fallback value used when primary input is absent.
    
        Returns:
            A value compatible with `float`.
    """
    raw = os.getenv(name)
    if raw is None:
        return default
    return float(raw)


def _env_bool(name: str, default: bool) -> bool:
    """Synchronous execution path for `_env_bool`.
    
    This callable is implemented in `src/document_analyzer_api/config/settings.py` and contributes to module-level behavior
    with explicit and testable execution semantics.
    
        Behavior:
            Coordinates helper calls (getenv, lower, strip) to satisfy the callable contract.
    
        Args:
            name: Identifier/environment key consumed by this callable.
            default: Fallback value used when primary input is absent.
    
        Returns:
            A value compatible with `bool`.
    """
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class Settings:
    """Settings runtime settings model.
    
    This class is defined in `src/document_analyzer_api/config/settings.py` and encapsulates a single cohesive concern.
    It is intended to be composed through dependency injection and exercised by
    unit/integration tests with stable behavioral contracts.
    
    Notable attributes: mongodb_uri, mongodb_database, mongodb_vector_index_name, neo4j_uri, neo4j_user, neo4j_password, s3_endpoint.
    """
    mongodb_uri: str = field(default_factory=lambda: os.getenv("MONGODB_URI", "mongodb://mongodb:27017"))
    mongodb_database: str = field(default_factory=lambda: os.getenv("MONGODB_DATABASE", "document_analyzer"))
    mongodb_vector_index_name: str = field(default_factory=lambda: os.getenv("MONGODB_VECTOR_INDEX_NAME", "chunk_embedding_index"))
    neo4j_uri: str = field(default_factory=lambda: os.getenv("NEO4J_URI", "bolt://neo4j:7687"))
    neo4j_user: str = field(default_factory=lambda: os.getenv("NEO4J_USER", "neo4j"))
    neo4j_password: str = field(default_factory=lambda: os.getenv("NEO4J_PASSWORD", "neo4jpassword"))
    s3_endpoint: str = field(default_factory=lambda: os.getenv("S3_ENDPOINT", "minio:9000"))
    s3_access_key: str = field(default_factory=lambda: os.getenv("S3_ACCESS_KEY", "minioadmin"))
    s3_secret_key: str = field(default_factory=lambda: os.getenv("S3_SECRET_KEY", "minioadmin"))
    s3_bucket_raw: str = field(default_factory=lambda: os.getenv("S3_BUCKET_RAW", "documents-raw"))
    s3_bucket_output: str = field(default_factory=lambda: os.getenv("S3_BUCKET_OUTPUT", "documents-output"))
    s3_output_presign_ttl_seconds: int = field(default_factory=lambda: _env_int("S3_OUTPUT_PRESIGN_TTL_SECONDS", 3600))
    ollama_base_url: str = field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://ollama:11434"))
    ollama_embedding_model: str = field(default_factory=lambda: os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"))
    ollama_text_model: str = field(default_factory=lambda: os.getenv("OLLAMA_TEXT_MODEL", "qwen3.5:9b"))
    dependency_timeout_seconds: float = field(default_factory=lambda: _env_float("DEPENDENCY_TIMEOUT_SECONDS", 2.0))

    storage_root_path: str = field(default_factory=lambda: os.getenv("STORAGE_ROOT_PATH", ".data/raw"))
    done_extension: str = field(default_factory=lambda: os.getenv("DONE_EXTENSION", ".done"))
    max_files_per_request: int = field(default_factory=lambda: _env_int("MAX_FILES_PER_REQUEST", 0))
    max_file_size_bytes: int = field(default_factory=lambda: _env_int("MAX_FILE_SIZE_BYTES", 0))
    max_total_payload_bytes: int = field(default_factory=lambda: _env_int("MAX_TOTAL_PAYLOAD_BYTES", 0))
    temp_chunk_ttl_seconds: int = field(default_factory=lambda: _env_int("TEMP_CHUNK_TTL_SECONDS", 600))
    chat_history_ttl_seconds: int = field(default_factory=lambda: _env_int("CHAT_HISTORY_TTL_SECONDS", 604800))
    chat_compaction_max_messages: int = field(default_factory=lambda: _env_int("CHAT_COMPACTION_MAX_MESSAGES", 20))
    default_top_k: int = field(default_factory=lambda: _env_int("DEFAULT_TOP_K", 8))
    default_min_score: float = field(default_factory=lambda: _env_float("DEFAULT_MIN_SCORE", 0.2))
    default_hybrid_alpha: float = field(default_factory=lambda: _env_float("DEFAULT_HYBRID_ALPHA", 0.5))
    default_audio_format: str = field(default_factory=lambda: os.getenv("DEFAULT_AUDIO_FORMAT", "wav"))
    default_tts_model: str = field(default_factory=lambda: os.getenv("DEFAULT_TTS_MODEL", "Qwen/Qwen3-TTS-12Hz-0.6B-Base"))
    default_tts_voice: str = field(default_factory=lambda: os.getenv("DEFAULT_TTS_VOICE", "alloy"))
    tts_api_base_url: str = field(default_factory=lambda: os.getenv("TTS_API_BASE_URL", "http://localhost:8010"))
    image_api_base_url: str = field(default_factory=lambda: os.getenv("IMAGE_API_BASE_URL", "http://localhost:8002"))
    image_model: str = field(default_factory=lambda: os.getenv("IMAGE_MODEL", "image-default"))
    ollama_image_model: str = field(default_factory=lambda: os.getenv("OLLAMA_IMAGE_MODEL", "llava"))
    provider_retry_count: int = field(default_factory=lambda: _env_int("PROVIDER_RETRY_COUNT", 2))
    provider_timeout_seconds: float = field(default_factory=lambda: _env_float("PROVIDER_TIMEOUT_SECONDS", 2.0))
    provider_backoff_seconds: float = field(default_factory=lambda: _env_float("PROVIDER_BACKOFF_SECONDS", 0.05))
    tracing_enabled: bool = field(default_factory=lambda: _env_bool("TRACING_ENABLED", True))
    tracing_service_name: str = field(default_factory=lambda: os.getenv("TRACING_SERVICE_NAME", "document-analyzer-api"))
    tracing_otlp_endpoint: str = field(default_factory=lambda: os.getenv("TRACING_OTLP_ENDPOINT", "jaeger:4317"))
    tracing_sample_ratio: float = field(default_factory=lambda: _env_float("TRACING_SAMPLE_RATIO", 1.0))

    def validate_runtime(self) -> None:
        """Synchronous execution path for `validate_runtime`.
        
        This callable is implemented in `src/document_analyzer_api/config/settings.py` and contributes to module-level behavior
        with explicit and testable execution semantics.
        
            Behavior:
                Validates inputs and raises explicit failures when invariants are violated.
        
            Args:
                None.
        
            Returns:
                A value compatible with `None`.
        """
        if self.provider_retry_count < 0:
            raise ValueError("PROVIDER_RETRY_COUNT must be >= 0")
        if self.provider_timeout_seconds <= 0:
            raise ValueError("PROVIDER_TIMEOUT_SECONDS must be > 0")
        if self.provider_backoff_seconds < 0:
            raise ValueError("PROVIDER_BACKOFF_SECONDS must be >= 0")
        if self.s3_output_presign_ttl_seconds <= 0:
            raise ValueError("S3_OUTPUT_PRESIGN_TTL_SECONDS must be > 0")
        if self.tracing_sample_ratio < 0 or self.tracing_sample_ratio > 1:
            raise ValueError("TRACING_SAMPLE_RATIO must be between 0 and 1")


        required_values = {
            "MONGODB_URI": self.mongodb_uri,
            "MONGODB_DATABASE": self.mongodb_database,
            "NEO4J_URI": self.neo4j_uri,
            "NEO4J_USER": self.neo4j_user,
            "NEO4J_PASSWORD": self.neo4j_password,
            "S3_ENDPOINT": self.s3_endpoint,
            "S3_ACCESS_KEY": self.s3_access_key,
            "S3_SECRET_KEY": self.s3_secret_key,
            "S3_BUCKET_RAW": self.s3_bucket_raw,
            "S3_BUCKET_OUTPUT": self.s3_bucket_output,
            "OLLAMA_BASE_URL": self.ollama_base_url,
            "OLLAMA_EMBEDDING_MODEL": self.ollama_embedding_model,
            "OLLAMA_TEXT_MODEL": self.ollama_text_model,
            "TTS_API_BASE_URL": self.tts_api_base_url,
            "IMAGE_API_BASE_URL": self.image_api_base_url,
            "IMAGE_MODEL": self.image_model,
            "DEFAULT_TTS_MODEL": self.default_tts_model,
            "DEFAULT_TTS_VOICE": self.default_tts_voice,
        }

        missing = [key for key, value in required_values.items() if not str(value).strip()]
        if missing:
            names = ", ".join(missing)
            raise ValueError(f"Missing required settings for real mode: {names}")








