from fastapi import APIRouter, File, HTTPException, UploadFile

from ...core.store import save_profile
from ...services.chunker import ProfileChunker
from ...services.parser import ResumeParser

router = APIRouter()
parser = ResumeParser()
chunker = ProfileChunker()


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")
    ext = file.filename.lower().split(".")[-1]
    if ext not in ("pdf", "docx", "doc"):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")
    try:
        profile, raw_text = parser.parse(file.filename, content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    chunks = chunker.chunk(profile)
    save_profile(profile)
    return {"profile": profile.model_dump(), "profile_id": profile.id, "chunks": chunks}
