import logging

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_current_user
from app.core.logging import log_safe
from app.core.storage import get_storage
from app.core.storage_files import get_storage_client
from app.models.schemas import Job, TailoredResume
from app.services.tailor import TailorService

logger = logging.getLogger(__name__)

router = APIRouter()
tailor_service = TailorService()
storage = get_storage()
storage_client = get_storage_client()


@router.get("/apply-kit/{profile_id}/{job_id}")
async def apply_kit(
    profile_id: str,
    job_id: str,
    user: dict | None = Depends(get_current_user),
) -> dict:
    """Generate an apply kit (tailored resume + cover letter). No auto-submit."""
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

    cover_letter = ""
    cover_letter_path = None
    try:
        prompt = (
            "Write a concise, honest cover letter for this job using only facts from the profile.\n"
            "Return only the cover letter text, no markdown fences.\n\n"
            f"Job: {job.model_dump_json()}\n\nProfile: {profile.model_dump_json()}"
        )
        cover_letter = await tailor_service.llm.complete(prompt)

        pdf_bytes = cover_letter.encode("utf-8")
        upload_result = await storage_client.upload_cover_letter(
            pdf_bytes,
            f"cover-letter-{profile_id}-{job_id}.txt",
            user_id or "anonymous",
            content_type="text/plain",
        )
        cover_letter_path = upload_result["path"]
    except Exception as exc:
        log_safe(logger, "Cover letter generation failed", error=str(exc)[:200])

    return {
        "job_id": job_id,
        "profile_id": profile_id,
        "user_id": user_id,
        "tailored_resume": tailored.model_dump(),
        "cover_letter": cover_letter,
        "cover_letter_path": cover_letter_path,
        "note": "Kit generated for manual submission. No auto-submit.",
    }
