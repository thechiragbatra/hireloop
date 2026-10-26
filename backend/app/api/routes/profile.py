from fastapi import APIRouter, HTTPException

from ...core.store import get_profile, save_profile
from ...models.schemas import Profile
from ...services.chunker import ProfileChunker

router = APIRouter()
chunker = ProfileChunker()


@router.get("/profile/{profile_id}")
async def get_profile_route(profile_id: str):
    profile = get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile.model_dump()


@router.put("/profile/{profile_id}")
async def put_profile_route(profile_id: str, profile: Profile):
    profile.id = profile_id
    save_profile(profile)
    return profile.model_dump()


@router.post("/profile/{profile_id}/rechunk")
async def rechunk_profile_route(profile_id: str):
    profile = get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    chunks = chunker.chunk(profile)
    return {"chunks": chunks}
