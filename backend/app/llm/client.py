from typing import Any, Optional, Type
from pydantic import BaseModel

class LLMClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "cheap-model"):
        self.api_key = api_key
        self.model = model

    async def structured(self, prompt: str, schema: Type[BaseModel], **kwargs) -> BaseModel:
        # Placeholder for structured output
        # In practice use provider with JSON/schema enforcement
        instance = schema()
        return instance

    async def complete(self, prompt: str, **kwargs) -> str:
        return ""
