from abc import ABC, abstractmethod

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
