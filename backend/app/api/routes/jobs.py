from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.core.auth import get_current_user
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


class JobsFilter(BaseModel):
    source: str | None = None
    company: str | None = None
    query: str | None = None
    location: str | None = None
    limit: int = 20


@router.get("/jobs")
async def jobs(
    source: str | None = None,
    company: str | None = None,
    query: str | None = None,
    location: str | None = Query(default=None),
    limit: int = Query(default=20),
    user: dict | None = Depends(get_current_user),
) -> dict:
    adapters = [ADAPTERS[source]] if source else list(ADAPTERS.values())
    if source and source not in ADAPTERS:
        raise HTTPException(status_code=400, detail=f"Unknown job source: {source}")
    filters: dict[str, object] = {
        "company": company,
        "query": query,
        "location": location,
        "limit": limit,
    }
    fetched: list[Job] = []
    for adapter in adapters:
        fetched.extend(await adapter.fetch(filters))
    user_id = user.get("sub") if user else None
    storage.save_jobs([j.model_dump() for j in fetched], user_id=user_id)
    return {"jobs": [j.model_dump() for j in fetched]}


@router.post("/match")
async def match(
    req: MatchRequest,
    user: dict | None = Depends(get_current_user),
) -> dict:
    user_id = user.get("sub") if user else None
    stored = storage.get_profile(req.profile_id, user_id=user_id)
    if stored is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    from app.models.schemas import Profile

    profile = Profile(**stored["data"])
    jobs_to_match = req.jobs or [Job(**j) for j in storage.list_jobs(user_id=user_id)]
    results = await matcher.match(profile, jobs_to_match)
    return {"matches": [r.model_dump() for r in results]}
