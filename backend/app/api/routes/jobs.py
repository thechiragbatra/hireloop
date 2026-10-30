import asyncio
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from ...core.auth import get_current_user
from ...core.storage import get_storage
from ...models.schemas import Job, Profile
from ...services.job_sources import ADAPTERS
from ...services.matcher import Matcher

router = APIRouter()
storage = get_storage()
matcher = Matcher()


@router.post("/jobs")
async def fetch_jobs(filters: dict[str, Any] | None = None, user: dict = Depends(get_current_user)):
    filters = filters or {}
    owner = user["sub"]
    profile_id = filters.pop("profile_id", None)
    profile = None
    if profile_id:
        saved_profile = storage.get_profile(profile_id, user_id=owner)
        if not saved_profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        profile = Profile(**saved_profile["data"])
    all_jobs = []
    responses = await asyncio.gather(
        *(adapter.fetch(filters) for adapter in ADAPTERS.values()), return_exceptions=True
    )
    for jobs in responses:
        if isinstance(jobs, BaseException):
            continue
        all_jobs.extend(jobs)

    seen = set()
    unique = []
    for job in all_jobs:
        key = (job.title.lower(), job.company.lower())
        if key in seen:
            continue
        seen.add(key)
        storage.save_job(job.id, job.model_dump(mode="json"), user_id=owner)
        unique.append(job)

    query = str(filters.get("query") or "").strip().lower()
    if query:
        query_terms = [term for term in query.split() if len(term) > 1]
        unique = [
            job
            for job in unique
            if any(
                term in f"{job.title} {job.company} {job.description}".lower()
                for term in query_terms
            )
        ]
    if profile:
        scores = {r.job_id: r for r in await matcher.match(profile, unique)}
        unique.sort(key=lambda job: scores[job.id].score, reverse=True)
        response = [
            {
                **job.model_dump(mode="json"),
                "match_score": scores[job.id].score,
                "match_reasons": scores[job.id].reasons,
                "missing_skills": scores[job.id].missing_skills,
            }
            for job in unique[:100]
        ]
    else:
        response = [{**job.model_dump(mode="json"), "match_score": None} for job in unique[:100]]
    return {"jobs": response}


@router.get("/jobs")
async def list_jobs(user: dict = Depends(get_current_user)):
    return {"jobs": storage.list_jobs(user_id=user["sub"])}


@router.post("/match")
async def match_jobs(payload: dict[str, Any], user: dict = Depends(get_current_user)):
    profile_id = payload.get("profile_id")
    saved_profile = storage.get_profile(profile_id, user_id=user["sub"]) if profile_id else None
    if not saved_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile = Profile(**saved_profile["data"])
    jobs = [Job(**item) for item in payload.get("jobs", [])]
    if not jobs:
        jobs = [Job(**item) for item in storage.list_jobs(user_id=user["sub"])]
    results = await matcher.match(profile, jobs)
    return {
        "matches": [
            {
                **r.model_dump(),
                "job": next((j.model_dump() for j in jobs if j.id == r.job_id), None),
            }
            for r in results
        ]
    }
