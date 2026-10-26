from fastapi import APIRouter
from typing import Any

from ...models.schemas import Job
from ...services.job_sources import ADAPTERS

router = APIRouter()


@router.post("/jobs")
async def fetch_jobs(filters: dict[str, Any] | None = None):
    filters = filters or {}
    adapter = ADAPTERS.get("remoteok")
    if not adapter:
        return {"jobs": []}
    jobs = await adapter.fetch(filters)
    # Add simple match scores
    result = []
    for job in jobs:
        result.append({
            **job.model_dump(),
            "match_score": 75 + hash(job.id) % 20
        })
    return {"jobs": result}
