import logging
from typing import cast

from app.core.config import get_llm_client
from app.core.logging import log_safe
from app.llm.client import FakeLLMClient, LLMClient
from app.llm.prompts import TAILOR_RESUME_PROMPT
from app.models.schemas import Job, TailoredBullet, TailoredResume
from app.services.chunker import ProfileChunker

logger = logging.getLogger(__name__)


class TailorService:
    def __init__(self, llm: LLMClient | None = None, chunker: ProfileChunker | None = None):
        self.llm = llm or get_llm_client()
        self.chunker = chunker or ProfileChunker()

    async def tailor(self, profile, job: Job) -> TailoredResume:
        chunks = self.chunker.chunk(profile)
        if isinstance(self.llm, FakeLLMClient) or not chunks:
            return self._fallback(profile, job, chunks)
        try:
            prompt = TAILOR_RESUME_PROMPT.format(
                job=job.model_dump_json(),
                chunks=self._format_chunks(chunks),
            )
            result = cast(
                TailoredResume, await self.llm.complete_structured(TailoredResume, prompt)
            )
            result.job_id = job.id
            return result
        except Exception as exc:  # noqa: BLE001
            log_safe(logger, "Tailoring failed", job_id=job.id, error=str(exc)[:200])
            return self._fallback(profile, job, chunks)

    def _format_chunks(self, chunks: list[dict]) -> str:
        lines = []
        for chunk in chunks:
            lines.append(f"[{chunk['id']}] {chunk['text']}  (source: {chunk['source']})")
        return "\n".join(lines)

    def _fallback(self, profile, job: Job, chunks: list[dict]) -> TailoredResume:
        bullets = [TailoredBullet(text=chunk["text"], source_ids=[chunk["id"]]) for chunk in chunks]
        return TailoredResume(job_id=job.id, bullets=bullets, summary=None)
