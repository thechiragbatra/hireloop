from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.storage import get_storage
from app.services.parser import ResumeParser

router = APIRouter()
parser = ResumeParser()
storage = get_storage()


@router.post("/upload")
async def upload(file: UploadFile = File(...)) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    content = await file.read()
    try:
        profile, raw_text = await parser.parse(file.filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    storage.save_profile(profile.id, raw_text, profile.model_dump())
    return {"profile": profile.model_dump(), "raw_text": raw_text}
