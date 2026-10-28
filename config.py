
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env before LangChain initializes tracing.
load_dotenv()


class Settings(BaseSettings):
    app_name: str = "EnterpriseFlow AI"
    app_version: str = "0.1.0"
    environment: str = "development"

    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_model: str = "openrouter/free"
    openrouter_embedding_model: str = (
        "nvidia/nemotron-3.5-embed-1b:free"
    )

    # Legacy Hugging Face settings
    hf_token: str = Field(
        default="",
        validation_alias="HF_TOKEN",
    )
    hf_embedding_model: str = Field(
        default="BAAI/bge-small-en-v1.5",
        validation_alias="HF_EMBEDDING_MODEL",
    )

    # ChromaDB
    chroma_path: str = Field(
        default="./data/chroma",
        validation_alias="CHROMA_PATH",
    )

    # Redis caching
    redis_url: str = ""
    cache_enabled: bool = True
    cache_ttl_seconds: int = 600

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
