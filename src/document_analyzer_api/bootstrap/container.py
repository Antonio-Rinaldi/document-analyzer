from dataclasses import dataclass

from ..application.services.base_chunk_builder_service import BaseChunkBuilderService
from ..application.services.audio_service import AudioService
from ..application.services.chat_service import ChatService
from ..application.services.chunking_service import ChunkingService
from ..application.services.document_ingestion_service import DocumentIngestionService
from ..application.services.document_generation_service import DocumentGenerationService
from ..application.services.document_processing_pipeline_service import DocumentProcessingPipelineService
from ..application.services.document_query_service import DocumentQueryService
from ..application.services.document_summary_service import DocumentSummaryService
from ..application.services.image_service import ImageService
from ..application.services.retrieval_service import RetrievalService
from ..application.services.health_service import HealthService
from ..config.settings import Settings
from ..infrastructure.chunking.deterministic_summarizer import DeterministicSummarizer
from ..infrastructure.chunking.ollama_summarizer import OllamaSummarizer
from ..infrastructure.embeddings.deterministic_embedding_client import DeterministicEmbeddingClient
from ..infrastructure.embeddings.ollama_embedding_client import OllamaEmbeddingClient
from ..infrastructure.health.minio_health_adapter import MinioHealthAdapter
from ..infrastructure.health.mongo_health_adapter import MongoHealthAdapter
from ..infrastructure.health.neo4j_health_adapter import Neo4jHealthAdapter
from ..infrastructure.health.ollama_health_adapter import OllamaHealthAdapter
from ..infrastructure.modalities.local_image_provider import LocalImageProvider
from ..infrastructure.modalities.local_tts_provider import LocalTTSProvider
from ..infrastructure.modalities.http_image_provider import HttpImageProvider
from ..infrastructure.modalities.http_tts_provider import HttpTTSProvider
from ..infrastructure.modalities.ollama_image_provider import OllamaImageProvider
from ..infrastructure.parsing.markitdown_document_creator import MarkItDownDocumentCreator
from ..infrastructure.parsing.markitdown_document_parser import MarkItDownDocumentParser
from ..infrastructure.persistence.local_chunk_repository import LocalChunkRepository
from ..infrastructure.persistence.local_chat_session_repository import LocalChatSessionRepository
from ..infrastructure.persistence.local_document_metadata_repository import LocalDocumentMetadataRepository
from ..infrastructure.persistence.mongo_chat_session_repository import MongoChatSessionRepository
from ..infrastructure.persistence.mongo_chunk_repository import MongoChunkRepository
from ..infrastructure.persistence.mongo_document_metadata_repository import MongoDocumentMetadataRepository
from ..infrastructure.persistence.neo4j_chunk_repository import Neo4jChunkRepository
from ..infrastructure.retrieval.local_retrieval_backends import LocalGraphRetrievalBackend
from ..infrastructure.retrieval.local_retrieval_backends import LocalHybridRetrievalBackend
from ..infrastructure.retrieval.local_retrieval_backends import LocalVectorRetrievalBackend
from ..infrastructure.retrieval.mongo_vector_retrieval_backend import MongoVectorRetrievalBackend
from ..infrastructure.retrieval.neo4j_graph_retrieval_backend import Neo4jGraphRetrievalBackend
from ..infrastructure.retrieval.hybrid_retrieval_backend import HybridRetrievalBackend
from ..infrastructure.resilience.provider_wrappers import RetryEmbeddingClient
from ..infrastructure.resilience.provider_wrappers import RetrySummarizer
from ..infrastructure.storage.local_document_storage import LocalDocumentStorage
from ..infrastructure.storage.local_output_storage import LocalOutputStorage
from ..infrastructure.storage.s3_document_storage import S3DocumentStorage
from ..infrastructure.storage.s3_output_storage import S3OutputStorage
from ..infrastructure.text_generation.local_text_generation_client import LocalTextGenerationClient
from ..infrastructure.text_generation.ollama_text_generation_client import OllamaTextGenerationClient


@dataclass(slots=True)
class AppContainer:
    settings: Settings
    health_service: HealthService
    ingestion_service: DocumentIngestionService
    document_query_service: DocumentQueryService
    retrieval_service: RetrievalService
    generation_service: DocumentGenerationService
    summary_service: DocumentSummaryService
    chat_service: ChatService
    audio_service: AudioService
    image_service: ImageService
    base_chunk_builder_service: BaseChunkBuilderService
    chunking_service: ChunkingService

    @classmethod
    def from_settings(cls, settings: Settings) -> "AppContainer":
        retrieval_backends = (
            LocalVectorRetrievalBackend(root_path=settings.storage_root_path),
            LocalGraphRetrievalBackend(root_path=settings.storage_root_path),
            LocalHybridRetrievalBackend(root_path=settings.storage_root_path),
        )

        dependencies = [
            MongoHealthAdapter(uri=settings.mongodb_uri, timeout_seconds=settings.dependency_timeout_seconds),
            Neo4jHealthAdapter(
                uri=settings.neo4j_uri,
                user=settings.neo4j_user,
                password=settings.neo4j_password,
                timeout_seconds=settings.dependency_timeout_seconds,
            ),
            MinioHealthAdapter(
                endpoint=settings.s3_endpoint,
                access_key=settings.s3_access_key,
                secret_key=settings.s3_secret_key,
                timeout_seconds=settings.dependency_timeout_seconds,
            ),
            OllamaHealthAdapter(base_url=settings.ollama_base_url, timeout_seconds=settings.dependency_timeout_seconds),
        ]

        if settings.adapter_mode == "real":
            storage = S3DocumentStorage(
                endpoint=settings.s3_endpoint,
                access_key=settings.s3_access_key,
                secret_key=settings.s3_secret_key,
                bucket=settings.s3_bucket_raw,
                done_extension=settings.done_extension,
            )
            metadata_repository = MongoDocumentMetadataRepository(
                uri=settings.mongodb_uri,
                database=settings.mongodb_database,
            )
            repositories = [
                MongoChunkRepository(uri=settings.mongodb_uri, database=settings.mongodb_database),
                Neo4jChunkRepository(
                    uri=settings.neo4j_uri,
                    user=settings.neo4j_user,
                    password=settings.neo4j_password,
                ),
            ]
            summarizer = OllamaSummarizer(
                base_url=settings.ollama_base_url,
                model=settings.ollama_text_model,
            )
            embedding_client = OllamaEmbeddingClient(
                base_url=settings.ollama_base_url,
                model=settings.ollama_embedding_model,
            )
            output_storage = S3OutputStorage(
                endpoint=settings.s3_endpoint,
                access_key=settings.s3_access_key,
                secret_key=settings.s3_secret_key,
                bucket=settings.s3_bucket_output,
            )
            text_generation_client = OllamaTextGenerationClient(
                base_url=settings.ollama_base_url,
                model=settings.ollama_text_model,
            )
            chat_repository = MongoChatSessionRepository(
                uri=settings.mongodb_uri,
                database=settings.mongodb_database,
            )
            tts_provider = HttpTTSProvider(
                base_url=settings.tts_api_base_url,
                model=settings.default_tts_model,
                voice=settings.default_tts_voice,
            )
            image_fallback_provider = HttpImageProvider(
                base_url=settings.image_api_base_url,
                model=settings.image_model,
            )
            image_provider = OllamaImageProvider(
                base_url=settings.ollama_base_url,
                model=settings.ollama_image_model,
                fallback=image_fallback_provider,
            )
        else:
            storage = LocalDocumentStorage(root_path=settings.storage_root_path, done_extension=settings.done_extension)
            metadata_repository = LocalDocumentMetadataRepository(root_path=settings.storage_root_path)
            repositories = [
                LocalChunkRepository(root_path=settings.storage_root_path, backend_name="mongo"),
                LocalChunkRepository(root_path=settings.storage_root_path, backend_name="neo4j"),
            ]
            summarizer = DeterministicSummarizer()
            embedding_client = DeterministicEmbeddingClient()
            output_storage = LocalOutputStorage(root_path=settings.storage_root_path)
            text_generation_client = LocalTextGenerationClient()
            chat_repository = LocalChatSessionRepository(root_path=settings.storage_root_path)
            tts_provider = LocalTTSProvider()
            image_provider = LocalImageProvider()

        base_chunk_builder_service = BaseChunkBuilderService()
        parser = MarkItDownDocumentParser()
        document_creator = MarkItDownDocumentCreator()
        retrying_summarizer = RetrySummarizer(
            summarizer,
            retries=settings.provider_retry_count,
            timeout_seconds=settings.provider_timeout_seconds,
            backoff_seconds=settings.provider_backoff_seconds,
        )
        retrying_embedding_client = RetryEmbeddingClient(
            embedding_client,
            retries=settings.provider_retry_count,
            timeout_seconds=settings.provider_timeout_seconds,
            backoff_seconds=settings.provider_backoff_seconds,
        )

        if settings.adapter_mode == "real":
            vector_backend = MongoVectorRetrievalBackend(
                uri=settings.mongodb_uri,
                database=settings.mongodb_database,
                embedding_client=retrying_embedding_client,
                vector_index_name=settings.mongodb_vector_index_name,
            )
            graph_backend = Neo4jGraphRetrievalBackend(
                uri=settings.neo4j_uri,
                user=settings.neo4j_user,
                password=settings.neo4j_password,
            )
            hybrid_backend = HybridRetrievalBackend(vector_backend=vector_backend, graph_backend=graph_backend)
            retrieval_backends = (vector_backend, graph_backend, hybrid_backend)

        chunking_service = ChunkingService(summarizer=retrying_summarizer)
        retrieval_service = RetrievalService(
            vector_backend=retrieval_backends[0],
            graph_backend=retrieval_backends[1],
            hybrid_backend=retrieval_backends[2],
        )
        document_query_service = DocumentQueryService(metadata_repository=metadata_repository)
        generation_service = DocumentGenerationService(
            retrieval_service=retrieval_service,
            text_generation_client=text_generation_client,
        )
        audio_service = AudioService(generation_service=generation_service, tts_provider=tts_provider)
        image_service = ImageService(generation_service=generation_service, image_provider=image_provider)
        summary_service = DocumentSummaryService(
            query_service=document_query_service,
            output_storage=output_storage,
            document_creator=document_creator,
        )
        chat_service = ChatService(
            repository=chat_repository,
            generation_service=generation_service,
            chat_ttl_seconds=settings.chat_history_ttl_seconds,
            max_messages_before_compaction=settings.chat_compaction_max_messages,
        )
        processing_pipeline = DocumentProcessingPipelineService(
            parser=parser,
            base_chunk_builder=base_chunk_builder_service,
            chunking_service=chunking_service,
            embedding_client=retrying_embedding_client,
            repositories=repositories,
            metadata_repository=metadata_repository,
            temp_ttl_seconds=settings.temp_chunk_ttl_seconds,
        )

        return cls(
            settings=settings,
            health_service=HealthService(dependencies=dependencies),
            ingestion_service=DocumentIngestionService(
                storage=storage,
                pipeline=processing_pipeline,
                supported_extensions=parser.supported_extensions(),
            ),
            document_query_service=document_query_service,
            retrieval_service=retrieval_service,
            generation_service=generation_service,
            summary_service=summary_service,
            chat_service=chat_service,
            audio_service=audio_service,
            image_service=image_service,
            base_chunk_builder_service=base_chunk_builder_service,
            chunking_service=chunking_service,
        )









