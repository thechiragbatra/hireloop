from fastapi import APIRouter, Depends, HTTPException

from ...core.auth import get_current_user
from ...core.storage import get_storage
from ...models.schemas import Profile
from ...services.chunker import ProfileChunker

router = APIRouter()
chunker = ProfileChunker()
storage = get_storage()


@router.get("/profile/{profile_id}")
async def get_profile_route(profile_id: str, user: dict = Depends(get_current_user)):
    record = storage.get_profile(profile_id, user_id=user["sub"])
    if not record:
        raise HTTPException(status_code=404, detail="Profile not found")
    return record["data"]


@router.put("/profile/{profile_id}")
async def put_profile_route(
    profile_id: str, profile: Profile, user: dict = Depends(get_current_user)
):
    profile.id = profile_id
    storage.save_profile(
        profile_id, profile_data=profile.model_dump(mode="json"), user_id=user["sub"]
    )
    return profile.model_dump()


@router.post("/profile/{profile_id}/rechunk")
async def rechunk_profile_route(profile_id: str, user: dict = Depends(get_current_user)):
    record = storage.get_profile(profile_id, user_id=user["sub"])
    if not record:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile = Profile(**record["data"])
    chunks = chunker.chunk(profile)
    return {"chunks": chunks}
