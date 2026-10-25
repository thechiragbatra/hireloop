from ..llm.client import LLMClient
from ..models.schemas import JobPosting, MatchResult, ResumeProfile


class Matcher:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def match(self, profile: ResumeProfile, jobs: list[JobPosting]) -> list[MatchResult]:
        results: list[MatchResult] = []
        for job in jobs:
            # Cost funnel placeholder - rules/filter first
            mr = MatchResult(job_id=job.job_id, job=job, final_score=0.0)
            results.append(mr)
        return results
