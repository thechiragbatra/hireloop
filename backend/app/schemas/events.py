from typing import Any, Literal

from pydantic import BaseModel, Field


class RunEvent(BaseModel):
    run_id: str = Field(description="Run identifier")
    node: str = Field(description="Pipeline node name")
    status: Literal["started", "progress", "completed", "failed", "waiting_for_human"] = Field(
        description="Event status"
    )
    items_in: int | None = Field(default=None, description="Input count")
    items_out: int | None = Field(default=None, description="Output count")
    duration_ms: int | None = Field(default=None, description="Duration in milliseconds")
    cost_usd: float | None = Field(default=None, description="Cost in USD")
    message: str | None = Field(default=None, description="Short message without PII")
    meta: dict[str, Any] | None = Field(default=None, description="Additional metadata with no text")
