from abc import ABC, abstractmethod
from typing import Any, cast

import httpx
from pydantic import BaseModel


class LLMClient(ABC):
    """Provider-agnostic LLM client interface."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None, timeout: int = 60):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout

    @abstractmethod
    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion."""
        raise NotImplementedError

    @abstractmethod
    async def complete_structured(
        self, schema: type[BaseModel], prompt: str, **kwargs
    ) -> BaseModel:
        """Generate structured output conforming to schema."""
        raise NotImplementedError


class FakeLLMClient(LLMClient):
    """Fake LLM client for tests - no real API calls."""

    async def complete(self, prompt: str, **kwargs) -> str:
        return "fake response"

    async def complete_structured(
        self, schema: type[BaseModel], prompt: str, **kwargs
    ) -> BaseModel:
        # Return default instance
        return schema()


class OpenRouterLLMClient(LLMClient):
    """OpenRouter client (OpenAI-compatible chat completions)."""

    def __init__(
        self, api_key: str, base_url: str | None = None, timeout: int = 60, model: str | None = None
    ):
        super().__init__(api_key=api_key, base_url=base_url, timeout=timeout)
        self.base_url = base_url or "https://openrouter.ai/api/v1"
        self.model = model or "mistralai/mistral-small-latest"
        self._client = httpx.AsyncClient(timeout=timeout)

    async def _chat(self, messages: list[dict[str, str]], **kwargs) -> dict[str, Any]:
        headers: dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "messages": messages,
            **kwargs,
        }
        resp = await self._client.post(
            f"{self.base_url}/chat/completions", headers=headers, json=body
        )
        resp.raise_for_status()
        return cast(dict[str, Any], resp.json())

    async def complete(self, prompt: str, **kwargs) -> str:
        data = await self._chat([{"role": "user", "content": prompt}], **kwargs)
        return cast(str, data["choices"][0]["message"]["content"])

    async def complete_structured(
        self, schema: type[BaseModel], prompt: str, **kwargs
    ) -> BaseModel:
        data = await self._chat(
            [
                {
                    "role": "system",
                    "content": "Return only valid JSON matching the requested schema.",
                },
                {"role": "user", "content": prompt},
            ],
            **kwargs,
        )
        content = data["choices"][0]["message"]["content"]
        return schema.model_validate_json(content)

    async def aclose(self) -> None:
        await self._client.aclose()


class OpenAILLMClient(OpenRouterLLMClient):
    """OpenAI client (reuses OpenAI-compatible chat completions)."""

    def __init__(
        self, api_key: str, base_url: str | None = None, timeout: int = 60, model: str | None = None
    ):
        super().__init__(
            api_key=api_key,
            base_url=base_url or "https://api.openai.com/v1",
            timeout=timeout,
            model=model or "gpt-4o-mini",
        )


class AnthropicLLMClient(LLMClient):
    """Anthropic Messages API client."""

    def __init__(
        self, api_key: str, base_url: str | None = None, timeout: int = 60, model: str | None = None
    ):
        super().__init__(api_key=api_key, base_url=base_url, timeout=timeout)
        self.base_url = base_url or "https://api.anthropic.com"
        self.model = model or "claude-3-5-sonnet-20241022"
        self._client = httpx.AsyncClient(timeout=timeout)

    async def _messages(self, prompt: str, **kwargs) -> dict[str, Any]:
        headers: dict[str, str] = {
            "x-api-key": cast(str, self.api_key),
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "max_tokens": kwargs.pop("max_tokens", 1024),
            "messages": [{"role": "user", "content": prompt}],
            **kwargs,
        }
        resp = await self._client.post(f"{self.base_url}/v1/messages", headers=headers, json=body)
        resp.raise_for_status()
        return cast(dict[str, Any], resp.json())

    async def complete(self, prompt: str, **kwargs) -> str:
        data = await self._messages(prompt, **kwargs)
        return "".join(block.get("text", "") for block in data.get("content", []))

    async def complete_structured(
        self, schema: type[BaseModel], prompt: str, **kwargs
    ) -> BaseModel:
        data = await self._messages(
            f"Return only valid JSON matching the requested schema.\n\n{prompt}",
            **kwargs,
        )
        content = "".join(block.get("text", "") for block in data.get("content", []))
        return schema.model_validate_json(content)

    async def aclose(self) -> None:
        await self._client.aclose()


def build_llm_client(
    provider: str,
    api_key: str | None,
    base_url: str | None = None,
    timeout: int = 60,
    model: str | None = None,
) -> LLMClient:
    """Build an LLM client for the given provider.

    Falls back to FakeLLMClient when no API key is configured so the app
    stays runnable offline and tests remain hermetic.
    """
    if not api_key:
        return FakeLLMClient()
    provider = provider.lower()
    if provider in ("openrouter", "openai"):
        return (
            OpenRouterLLMClient(api_key=api_key, base_url=base_url, timeout=timeout, model=model)
            if provider == "openrouter"
            else OpenAILLMClient(api_key=api_key, base_url=base_url, timeout=timeout, model=model)
        )
    if provider == "anthropic":
        return AnthropicLLMClient(api_key=api_key, base_url=base_url, timeout=timeout, model=model)
    raise ValueError(f"Unsupported LLM provider: {provider}")
