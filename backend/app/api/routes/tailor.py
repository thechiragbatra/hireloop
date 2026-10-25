from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_current_user
from app.core.storage import get_storage
from app.models.schemas import Job, TailoredResume
from app.services.tailor import TailorService

router = APIRouter()
tailor_service = TailorService()
storage = get_storage()


@router.post("/tailor")
async def tailor(
    profile_id: str,
    job_id: str,
    user: dict | None = Depends(get_current_user),
) -> dict:
    user_id = user.get("sub") if user else None
    stored_profile = storage.get_profile(profile_id, user_id=user_id)
    if stored_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    stored_job = storage.get_job(job_id, user_id=user_id)
    if stored_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    from app.models.schemas import Profile

    profile = Profile(**stored_profile["data"])
    job = Job(**stored_job)
    tailored: TailoredResume = await tailor_service.tailor(profile, job)
    return tailored.model_dump()
