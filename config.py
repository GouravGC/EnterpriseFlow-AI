
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EnterpriseFlow AI"
    app_version: str = "0.1.0"
    environment: str = "development"

    # OpenRouter chat model
    openrouter_api_key: str = ""
    openrouter_model: str = "openrouter/free"

    # OpenRouter embedding model
    openrouter_embedding_model: str = (
        "nvidia/nemotron-3.5-embed-1b:free"
    )

    # Legacy Hugging Face settings retained for compatibility
    hf_token: str = Field(
        default="",
        validation_alias="HF_TOKEN",
    )
    hf_embedding_model: str = Field(
        default="BAAI/bge-small-en-v1.5",
        validation_alias="HF_EMBEDDING_MODEL",
    )

    # ChromaDB storage
    chroma_path: str = Field(
        default="./data/chroma",
        validation_alias="CHROMA_PATH",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
