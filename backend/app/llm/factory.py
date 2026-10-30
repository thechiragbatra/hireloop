from .client import LLMClient


def build_llm_client(
    provider: str = "openrouter",
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
) -> LLMClient:
    from .client import build_llm_client as build

    return build(provider=provider, api_key=api_key, base_url=base_url, model=model)
