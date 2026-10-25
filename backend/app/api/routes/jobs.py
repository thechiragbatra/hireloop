from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.storage import get_storage
from app.models.schemas import Job
from app.services.job_sources import ADAPTERS
from app.services.matcher import Matcher

router = APIRouter()
matcher = Matcher()
storage = get_storage()


class MatchRequest(BaseModel):
    profile_id: str
    jobs: list[Job] = []


@router.get("/jobs")
async def jobs(source: str | None = None) -> dict:
    adapters = [ADAPTERS[source]] if source else list(ADAPTERS.values())
    if source and source not in ADAPTERS:
        raise HTTPException(status_code=400, detail=f"Unknown job source: {source}")
    fetched: list[Job] = []
    for adapter in adapters:
        fetched.extend(await adapter.fetch({}))
    storage.save_jobs([j.model_dump() for j in fetched])
    return {"jobs": [j.model_dump() for j in fetched]}


@router.post("/match")
async def match(req: MatchRequest) -> dict:
    stored = storage.get_profile(req.profile_id)
    if stored is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    from app.models.schemas import Profile

    profile = Profile(**stored["data"])
    jobs_to_match = req.jobs or [Job(**j) for j in storage.list_jobs()]
    results = await matcher.match(profile, jobs_to_match)
    return {"matches": [r.model_dump() for r in results]}
