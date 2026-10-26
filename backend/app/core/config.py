from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False

    allowed_cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    database_url: str = "sqlite:///./data/hireloop.db"

    resume_ttl_seconds: int = 3600
    max_upload_mb: int = 10
    delete_on_session_end: bool = True

    llm_provider: str = "openrouter"
    llm_api_key: str = ""
    llm_base_url: str = "https://openrouter.ai/api/v1"
    cheap_model_name: str = "mistralai/mistral-small-latest"
    strong_model_name: str = "anthropic/claude-3.5-sonnet"

    shared_key_rate_limit_per_min: int = 10
    rate_limit_enabled: bool = True

    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"
    langsmith_api_key: str = ""
    langsmith_project: str = "hireloop"

    enable_adzuna: bool = False
    adzuna_app_id: str = ""
    adzuna_app_key: str = ""
    enable_remoteok: bool = True

    log_resume_text: bool = False

    supabase_url: str = ""
    supabase_publishable_key: str = ""
    supabase_secret_key: str = ""
    supabase_jwks_url: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
