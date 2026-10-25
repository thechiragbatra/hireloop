from typing import List
from ..models.schemas import MatchResult, JobPosting, ResumeProfile
from ..llm.client import LLMClient

class Matcher:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    async def match(self, profile: ResumeProfile, jobs: List[JobPosting]) -> List[MatchResult]:
        results: List[MatchResult] = []
        for job in jobs:
            # Cost funnel placeholder - rules/filter first
            mr = MatchResult(job_id=job.job_id, job=job, final_score=0.0)
            results.append(mr)
        return results
