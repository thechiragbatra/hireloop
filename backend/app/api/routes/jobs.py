from fastapi import APIRouter
from typing import Any

from ...models.schemas import Job
from ...services.job_sources import ADAPTERS

router = APIRouter()


@router.post("/jobs")
async def fetch_jobs(filters: dict[str, Any] | None = None):
    filters = filters or {}
    all_jobs = []
    for name, adapter in ADAPTERS.items():
        try:
            jobs = await adapter.fetch(filters)
            all_jobs.extend(jobs)
        except Exception:
            continue
    # Deduplicate by title+company
    seen = set()
    unique = []
    for job in all_jobs:
        key = (job.title.lower(), job.company.lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append({
            **job.model_dump(),
            "match_score": 75 + hash(job.id) % 25
        })
    return {"jobs": unique[:100]}
