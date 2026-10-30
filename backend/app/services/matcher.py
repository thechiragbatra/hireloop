import logging
import re
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
        fallback = {job.id: self._heuristic(profile, job) for job in jobs}
        if isinstance(self.llm, FakeLLMClient):
            return [fallback[job.id] for job in jobs]

        shortlist = sorted(jobs, key=lambda job: fallback[job.id].score, reverse=True)[:20]
        for job in shortlist:
            try:
                fallback[job.id] = await self._score(profile, job)
            except Exception as exc:  # noqa: BLE001
                log_safe(logger, "Match scoring failed", job_id=job.id, error=str(exc)[:200])
        return sorted(
            (fallback[job.id] for job in jobs), key=lambda result: result.score, reverse=True
        )

    async def _score(self, profile: Profile, job: Job) -> MatchResult:
        if isinstance(self.llm, FakeLLMClient):
            return self._heuristic(profile, job)
        prompt = MATCH_SCORE_PROMPT.format(
            profile=profile.model_dump_json(),
            job=job.model_dump_json(),
        )
        scored = cast(MatchResult, await self.llm.complete_structured(MatchResult, prompt))
        scored.job_id = job.id
        scored.score = max(0.0, min(100.0, float(scored.score)))
        return scored

    def _heuristic(self, profile: Profile, job: Job) -> MatchResult:
        profile_terms = {skill.lower() for skill in profile.skills}
        resume_text = " ".join(
            [
                *profile.skills,
                *(bullet.text for exp in profile.experience for bullet in exp.bullets),
                *(bullet.text for project in profile.projects for bullet in project.bullets),
            ]
        ).lower()

        def terms(text: str) -> set[str]:
            return set(re.findall(r"[a-z0-9+#.]{2,}", text.lower()))

        required = {
            requirement.strip().lower() for requirement in job.requirements if requirement.strip()
        }
        matched = required & profile_terms
        missing = sorted(required - profile_terms)
        overlap = terms(job.title + " " + job.description) & terms(resume_text)
        skill_score = (len(matched) / len(required) * 75) if required else 0
        evidence_score = min(25, len(overlap) * 3)
        reasons = []
        if matched:
            reasons.append("Matching skills: " + ", ".join(sorted(matched)))
        if overlap:
            reasons.append(f"Resume evidence overlaps with {len(overlap)} job keywords")
        if not reasons:
            reasons.append("Not enough resume evidence to establish a strong match")
        return MatchResult(
            job_id=job.id,
            score=round(min(100, skill_score + evidence_score), 1),
            reasons=reasons,
            missing_skills=missing,
        )
