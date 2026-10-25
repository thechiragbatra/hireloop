
from ..llm.client import LLMClient
from ..models.schemas import Job, MatchResult, Profile


class Matcher:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def match(self, profile: Profile, jobs: list[Job]) -> list[MatchResult]:
        results: list[MatchResult] = []
        for job in jobs:
            results.append(
                MatchResult(
                    job_id=job.id,
                    score=0.0,
                    reasons=[],
                    missing_skills=[],
                )
            )
        return results
