from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.auth import get_current_user
from app.core.storage import get_storage
from app.core.storage_files import get_storage_client
from app.services.parser import ResumeParser

router = APIRouter()
parser = ResumeParser()
storage = get_storage()
storage_client = get_storage_client()


@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    user: dict | None = Depends(get_current_user),
) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    content = await file.read()
    user_id = user.get("sub") if user else None

    try:
        await storage_client.upload_resume(content, file.filename, user_id or "anonymous")
    except Exception:
        # Storage failure should not block parsing; continue with local parse
        pass

    try:
        profile, raw_text = await parser.parse(file.filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    storage.save_profile(profile.id, raw_text, profile.model_dump(), user_id=user_id)
    return {
        "profile": profile.model_dump(),
        "raw_text": raw_text,
        "user_id": user_id,
    }
