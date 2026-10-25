import logging
from typing import cast

from app.core.config import get_llm_client
from app.core.logging import log_safe
from app.llm.client import FakeLLMClient, LLMClient
from app.llm.prompts import MATCH_SCORE_PROMPT
from app.models.schemas import Job, MatchResult, Profile

logger = logging.getLogger(__name__)


class Matcher:
    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm or get_llm_client()

    async def match(self, profile: Profile, jobs: list[Job]) -> list[MatchResult]:
        results: list[MatchResult] = []
        for job in jobs:
            try:
                result = await self._score(profile, job)
            except Exception as exc:  # noqa: BLE001
                log_safe(logger, "Match scoring failed", job_id=job.id, error=str(exc)[:200])
                result = MatchResult(job_id=job.id, score=0.0, reasons=[], missing_skills=[])
            results.append(result)
        return results

    async def _score(self, profile: Profile, job: Job) -> MatchResult:
        if isinstance(self.llm, FakeLLMClient):
            return MatchResult(
                job_id=job.id,
                score=0.0,
                reasons=["LLM not configured"],
                missing_skills=list(job.requirements),
            )
        prompt = MATCH_SCORE_PROMPT.format(
            profile=profile.model_dump_json(),
            job=job.model_dump_json(),
        )
        scored = cast(MatchResult, await self.llm.complete_structured(MatchResult, prompt))
        scored.job_id = job.id
        scored.score = max(0.0, min(100.0, float(scored.score)))
        return scored
