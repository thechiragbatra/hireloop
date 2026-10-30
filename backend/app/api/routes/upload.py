from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ...core.auth import get_current_user
from ...core.storage import get_storage
from ...services.chunker import ProfileChunker
from ...services.parser import ResumeParser

router = APIRouter()
parser = ResumeParser()
chunker = ProfileChunker()
storage = get_storage()


@router.post("/upload")
async def upload(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")
    ext = file.filename.lower().split(".")[-1]
    if ext not in ("pdf", "docx"):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
    from ...core.config import get_settings

    max_bytes = get_settings().max_upload_mb * 1024 * 1024
    content = await file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(status_code=400, detail="File too large")
    try:
        profile, raw_text = parser.parse(file.filename, content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    chunks = chunker.chunk(profile)
    user_id = user["sub"]
    storage.save_profile(profile.id, profile_data=profile.model_dump(mode="json"), user_id=user_id)
    return {
        "profile": profile.model_dump(mode="json"),
        "profile_id": profile.id,
        "raw_text": raw_text,
        "chunks": chunks,
    }
