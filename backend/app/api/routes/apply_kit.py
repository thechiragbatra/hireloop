import logging

from fastapi import APIRouter, HTTPException

from app.core.logging import log_safe
from app.core.storage import get_storage
from app.llm.client import FakeLLMClient
from app.llm.prompts import COVER_LETTER_PROMPT
from app.models.schemas import Job, TailoredResume
from app.services.tailor import TailorService

logger = logging.getLogger(__name__)

router = APIRouter()
tailor_service = TailorService()
storage = get_storage()


@router.get("/apply-kit/{profile_id}/{job_id}")
async def apply_kit(profile_id: str, job_id: str) -> dict:
    """Generate an apply kit (tailored resume + cover letter). No auto-submit."""
    stored_profile = storage.get_profile(profile_id)
    if stored_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    stored_job = storage.get_job(job_id)
    if stored_job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    from app.models.schemas import Profile

    profile = Profile(**stored_profile["data"])
    job = Job(**stored_job)

    tailored: TailoredResume = await tailor_service.tailor(profile, job)

    cover_letter = ""
    try:
        if not isinstance(tailor_service.llm, FakeLLMClient):
            prompt = COVER_LETTER_PROMPT.format(
                job=job.model_dump_json(),
                profile=profile.model_dump_json(),
            )
            cover_letter = await tailor_service.llm.complete(prompt)
    except Exception as exc:  # noqa: BLE001
        log_safe(logger, "Cover letter generation failed", error=str(exc)[:200])
        cover_letter = ""

    return {
        "job_id": job_id,
        "profile_id": profile_id,
        "tailored_resume": tailored.model_dump(),
        "cover_letter": cover_letter,
        "note": "Kit generated for manual submission. No auto-submit.",
    }
