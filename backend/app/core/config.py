from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import os

class Settings(BaseSettings):
    app_name: str = "job-copilot"
    env: str = "dev"
    debug: bool = False
    session_ttl_minutes: int = 60
    job_cache_ttl_minutes: int = 60
    max_upload_mb: int = 10
    allowed_sources: List[str] = Field(default_factory=lambda: ["greenhouse", "lever", "ashby", "adzuna", "remoteok", "custom"])
    shared_llm_rate_limit_per_min: int = 10
    byok_header: str = "X-LLM-API-Key"
    faiss_index_dir: str = "./data/faiss"
    sqlite_url: str = "sqlite:///./data/jobcopilot.db"
    langfuse_public_key: Optional[str] = None
    langfuse_secret_key: Optional[str] = None
    langfuse_host: Optional[str] = None
    langsmith_api_key: Optional[str] = None
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
