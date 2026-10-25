from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.llm.client import LLMClient, build_llm_client


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Application ---
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False

    allowed_cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # --- Database (Supabase Postgres) ---
    database_url: str = "sqlite:///./data/hireloop.db"
    database_url_async: str = "sqlite+aiosqlite:///./data/hireloop.db"

    # --- Resume processing ---
    resume_ttl_seconds: int = 3600
    max_upload_mb: int = 10
    delete_on_session_end: bool = True

    # --- LLM Provider (bring-your-own-key supported) ---
    llm_provider: str = "openrouter"
    llm_api_key: str = ""
    llm_base_url: str = "https://openrouter.ai/api/v1"
    cheap_model_name: str = "mistralai/mistral-small-latest"
    strong_model_name: str = "anthropic/claude-3.5-sonnet"

    # --- Embeddings / Reranker (hosted, 512 MB limit) ---
    embedder_provider: str = "openrouter"
    embedder_api_key: str = ""
    embedder_base_url: str = "https://openrouter.ai/api/v1"
    embedder_model_name: str = "mistralai/mistral-small-latest"
    reranker_provider: str = "openrouter"
    reranker_api_key: str = ""
    reranker_base_url: str = "https://openrouter.ai/api/v1"
    reranker_model_name: str = "anthropic/claude-3.5-sonnet"

    # --- Rate limiting ---
    shared_key_rate_limit_per_min: int = 10
    rate_limit_enabled: bool = True

    # --- Observability ---
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"
    langsmith_api_key: str = ""
    langsmith_project: str = "hireloop"

    # --- Job sources (public only) ---
    enable_adzuna: bool = False
    adzuna_app_id: str = ""
    adzuna_app_key: str = ""
    enable_remoteok: bool = True

    # --- Supabase Auth ---
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""

    # --- Supabase Storage (private bucket, signed URLs) ---
    supabase_storage_bucket: str = "hireloop-resumes"
    supabase_storage_url: str = ""

    # --- Privacy ---
    log_resume_text: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_llm_client() -> LLMClient:
    settings = get_settings()
    return build_llm_client(
        provider=settings.llm_provider,
        api_key=settings.llm_api_key or None,
        base_url=settings.llm_base_url or None,
        model=settings.strong_model_name,
    )
