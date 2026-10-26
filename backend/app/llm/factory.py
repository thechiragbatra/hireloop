from .client import FakeLLMClient, LLMClient


def build_llm_client(provider: str = "openrouter", api_key: str | None = None, base_url: str | None = None, model: str | None = None) -> LLMClient:
    return FakeLLMClient()
