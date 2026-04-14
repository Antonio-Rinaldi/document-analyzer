"""Detailed module documentation for `src/document_analyzer_api/config/settings.py`.

File role:
- Located in the project layer.
- Defines logic and symbols for `settings.py` within Document Analyzer V1.

Purpose:
- Defines typed runtime configuration loaded from environment variables with validation guards.

Exported symbols overview:
- Classes: Settings.
- Functions: _env_int, _env_float, _env_bool.

Operational context:
- Behavior aligns with `documentation/REFINED_SPECS.md` and conventions in
  `documentation/REFINED_PROJECT_CONVENTIONS.md`.
- Contracts in this module are verified by the project test suite.
"""

import os
from dataclasses import dataclass


def _env_int(name: str, default: int) -> int:
    """Detailed synchronous function documentation for `_env_int`.
    
    This callable is implemented in `src/document_analyzer_api/config/settings.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            name: Environment variable or entity name, depending on callable context.
            default: Fallback value used when the primary source is not available.
    
        Returns:
            Value defined by `_env_int` contract and consumed by downstream callers.
    """
    raw = os.getenv(name)
    if raw is None:
        return default
    return int(raw)


def _env_float(name: str, default: float) -> float:
    """Detailed synchronous function documentation for `_env_float`.
    
    This callable is implemented in `src/document_analyzer_api/config/settings.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            name: Environment variable or entity name, depending on callable context.
            default: Fallback value used when the primary source is not available.
    
        Returns:
            Value defined by `_env_float` contract and consumed by downstream callers.
    """
    raw = os.getenv(name)
    if raw is None:
        return default
    return float(raw)


def _env_bool(name: str, default: bool) -> bool:
    """Detailed synchronous function documentation for `_env_bool`.
    
    This callable is implemented in `src/document_analyzer_api/config/settings.py` and contributes to the module workflow
    through deterministic input/output behavior and explicit collaboration contracts.
    
        Behavior:
            Executes the callable contract for this module responsibility.
    
        Args:
            name: Environment variable or entity name, depending on callable context.
            default: Fallback value used when the primary source is not available.
    
        Returns:
            Value defined by `_env_bool` contract and consumed by downstream callers.
    """
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class Settings:
    """Detailed class documentation for `Settings`.
    
    This runtime configuration model belongs to `src/document_analyzer_api/config/settings.py` and encapsulates one cohesive responsibility in the
    Document Analyzer architecture. It is designed for dependency-injected composition,
    explicit boundaries, stable contracts, and straightforward unit/integration testing.
    """
    adapter_mode: str = os.getenv("ADAPTER_MODE", "local")
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://mongodb:27017")
    mongodb_database: str = os.getenv("MONGODB_DATABASE", "document_analyzer")
    mongodb_vector_index_name: str = os.getenv("MONGODB_VECTOR_INDEX_NAME", "chunk_embedding_index")
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "neo4jpassword")
    s3_endpoint: str = os.getenv("S3_ENDPOINT", "minio:9000")
    s3_access_key: str = os.getenv("S3_ACCESS_KEY", "minioadmin")
    s3_secret_key: str = os.getenv("S3_SECRET_KEY", "minioadmin")
    s3_bucket_raw: str = os.getenv("S3_BUCKET_RAW", "documents-raw")
    s3_bucket_output: str = os.getenv("S3_BUCKET_OUTPUT", "documents-output")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    ollama_embedding_model: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    ollama_text_model: str = os.getenv("OLLAMA_TEXT_MODEL", "qwen3.5:9b")
    dependency_timeout_seconds: float = float(os.getenv("DEPENDENCY_TIMEOUT_SECONDS", "2.0"))

    storage_root_path: str = os.getenv("STORAGE_ROOT_PATH", ".data/raw")
    done_extension: str = os.getenv("DONE_EXTENSION", ".done")
    max_files_per_request: int = _env_int("MAX_FILES_PER_REQUEST", 0)
    max_file_size_bytes: int = _env_int("MAX_FILE_SIZE_BYTES", 0)
    max_total_payload_bytes: int = _env_int("MAX_TOTAL_PAYLOAD_BYTES", 0)
    temp_chunk_ttl_seconds: int = _env_int("TEMP_CHUNK_TTL_SECONDS", 600)
    chat_history_ttl_seconds: int = _env_int("CHAT_HISTORY_TTL_SECONDS", 604800)
    chat_compaction_max_messages: int = _env_int("CHAT_COMPACTION_MAX_MESSAGES", 20)
    default_top_k: int = _env_int("DEFAULT_TOP_K", 8)
    default_min_score: float = _env_float("DEFAULT_MIN_SCORE", 0.2)
    default_hybrid_alpha: float = _env_float("DEFAULT_HYBRID_ALPHA", 0.5)
    default_audio_format: str = os.getenv("DEFAULT_AUDIO_FORMAT", "wav")
    default_tts_model: str = os.getenv("DEFAULT_TTS_MODEL", "Qwen/Qwen3-TTS-12Hz-0.6B-Base")
    default_tts_voice: str = os.getenv("DEFAULT_TTS_VOICE", "alloy")
    tts_api_base_url: str = os.getenv("TTS_API_BASE_URL", "http://localhost:8010")
    image_api_base_url: str = os.getenv("IMAGE_API_BASE_URL", "http://localhost:8002")
    image_model: str = os.getenv("IMAGE_MODEL", "image-default")
    ollama_image_model: str = os.getenv("OLLAMA_IMAGE_MODEL", "llava")
    provider_retry_count: int = _env_int("PROVIDER_RETRY_COUNT", 2)
    provider_timeout_seconds: float = _env_float("PROVIDER_TIMEOUT_SECONDS", 2.0)
    provider_backoff_seconds: float = _env_float("PROVIDER_BACKOFF_SECONDS", 0.05)
    tracing_enabled: bool = _env_bool("TRACING_ENABLED", True)
    tracing_service_name: str = os.getenv("TRACING_SERVICE_NAME", "document-analyzer-api")
    tracing_otlp_endpoint: str = os.getenv("TRACING_OTLP_ENDPOINT", "jaeger:4317")
    tracing_sample_ratio: float = _env_float("TRACING_SAMPLE_RATIO", 1.0)

    def is_real_mode(self) -> bool:
        """Detailed synchronous function documentation for `is_real_mode`.
        
        This callable is implemented in `src/document_analyzer_api/config/settings.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Executes the callable contract for this module responsibility.
        
            Args:
                None.
        
            Returns:
                Value defined by `is_real_mode` contract and consumed by downstream callers.
        """
        return self.adapter_mode == "real"

    def validate_runtime(self) -> None:
        """Detailed synchronous function documentation for `validate_runtime`.
        
        This callable is implemented in `src/document_analyzer_api/config/settings.py` and contributes to the module workflow
        through deterministic input/output behavior and explicit collaboration contracts.
        
            Behavior:
                Validates inputs and raises explicit failures for invalid states.
        
            Args:
                None.
        
            Returns:
                Value defined by `validate_runtime` contract and consumed by downstream callers.
        """
        if self.adapter_mode not in {"local", "real"}:
            raise ValueError("ADAPTER_MODE must be 'local' or 'real'")

        if self.provider_retry_count < 0:
            raise ValueError("PROVIDER_RETRY_COUNT must be >= 0")
        if self.provider_timeout_seconds <= 0:
            raise ValueError("PROVIDER_TIMEOUT_SECONDS must be > 0")
        if self.provider_backoff_seconds < 0:
            raise ValueError("PROVIDER_BACKOFF_SECONDS must be >= 0")
        if self.tracing_sample_ratio < 0 or self.tracing_sample_ratio > 1:
            raise ValueError("TRACING_SAMPLE_RATIO must be between 0 and 1")

        if not self.is_real_mode():
            return

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








