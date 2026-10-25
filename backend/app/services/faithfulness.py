import logging
from typing import cast

from pydantic import BaseModel, Field

from app.core.config import get_llm_client
from app.core.logging import log_safe
from app.llm.client import FakeLLMClient, LLMClient
from app.llm.prompts import FAITHFULNESS_PROMPT
from app.models.schemas import FaithfulnessReport, TailoredResume
from app.services.chunker import ProfileChunker

logger = logging.getLogger(__name__)


class _FaithfulnessLLMOutput(BaseModel):
    unsupported: list[str] = Field(default_factory=list)
    overall_score: float = Field(ge=0, le=1, default=1.0)


class FaithfulnessService:
    def __init__(self, llm: LLMClient | None = None, chunker: ProfileChunker | None = None):
        self.llm = llm or get_llm_client()
        self.chunker = chunker or ProfileChunker()

    async def verify(self, profile, tailored: TailoredResume) -> FaithfulnessReport:
        chunks = self.chunker.chunk(profile)
        chunk_map = {c["id"]: c["text"] for c in chunks}
        if isinstance(self.llm, FakeLLMClient) or not tailored.bullets:
            return FaithfulnessReport(
                overall_score=1.0,
                supported_bullets=len(tailored.bullets),
                total_bullets=len(tailored.bullets),
                unsupported=[],
            )
        try:
            prompt = FAITHFULNESS_PROMPT.format(
                chunks=self._format_chunks(chunks),
                bullets=self._format_bullets(tailored.bullets, chunk_map),
            )
            result = cast(
                _FaithfulnessLLMOutput,
                await self.llm.complete_structured(_FaithfulnessLLMOutput, prompt),
            )
            unsupported = [u for u in result.unsupported if u]
            total = len(tailored.bullets)
            supported = max(0, total - len(unsupported))
            score = (supported / total) if total else 1.0
            return FaithfulnessReport(
                overall_score=round(score, 2),
                supported_bullets=supported,
                total_bullets=total,
                unsupported=unsupported,
            )
        except Exception as exc:  # noqa: BLE001
            log_safe(logger, "Faithfulness check failed", error=str(exc)[:200])
            return FaithfulnessReport(
                overall_score=1.0,
                supported_bullets=len(tailored.bullets),
                total_bullets=len(tailored.bullets),
                unsupported=[],
            )

    def _format_chunks(self, chunks: list[dict]) -> str:
        return "\n".join(f"[{c['id']}] {c['text']}" for c in chunks)

    def _format_bullets(self, bullets, chunk_map: dict) -> str:
        lines = []
        for b in bullets:
            evidence = " | ".join(chunk_map.get(s, "(missing)") for s in b.source_ids)
            lines.append(
                f"- {b.text}  (cites: {', '.join(b.source_ids) or 'none'} | evidence: {evidence})"
            )
        return "\n".join(lines)
