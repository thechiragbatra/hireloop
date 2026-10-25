from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Header, Request
from fastapi.responses import StreamingResponse
from typing import Optional
import io
import uuid
from datetime import datetime, timedelta

from ..core.config import settings
from ..core.privacy import PRIVACY_NOTICE, hash_ip
from ..core.rate_limit import check_rate_limit
from ..models.schemas import *
from ..services.parser import ResumeParser
from ..services.chunker import ProfileChunker
from ..services.tracker import TrackerService

router = APIRouter()
parser = ResumeParser()
chunker = ProfileChunker()
tracker = TrackerService()

@router.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}

@router.get("/privacy")
async def privacy():
    return {"notice": PRIVACY_NOTICE}

@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(request: Request, file: UploadFile = File(...), x_llm_api_key: Optional[str] = Header(None)):
    # Rate limit if using shared key (no BYO key)
    if not x_llm_api_key:
        ip = request.client.host if request.client else "unknown"
        if not check_rate_limit(ip, "/upload", settings.shared_llm_rate_limit_per_min):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
    content = await file.read()
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")
    try:
        profile, raw_text = parser.parse(file.filename or "resume", content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    session_id = str(uuid.uuid4())
    profile_id = str(uuid.uuid4())
    profile.profile_id = profile_id
    # Chunk
    chunks = chunker.chunk(profile)
    profile.chunks = chunks
    expires_at = datetime.utcnow() + timedelta(minutes=settings.session_ttl_minutes)
    return ResumeUploadResponse(session_id=session_id, profile_id=profile_id, status="parsed", expires_at=expires_at)

@router.get("/profile/{profile_id}", response_model=ResumeProfile)
async def get_profile(profile_id: str):
    # Placeholder
    return ResumeProfile(profile_id=profile_id)

@router.put("/profile/{profile_id}", response_model=ResumeProfile)
async def put_profile(profile_id: str, profile: ResumeProfile):
    profile.profile_id = profile_id
    # Rechunk
    profile.chunks = chunker.chunk(profile)
    return profile

@router.post("/profile/{profile_id}/rechunk")
async def rechunk_profile(profile_id: str, profile: ResumeProfile):
    profile.profile_id = profile_id
    chunks = chunker.chunk(profile)
    profile.chunks = chunks
    return {"chunks": chunks}

@router.get("/tracker")
async def list_tracker(profile_id: Optional[str] = None, status: Optional[str] = None):
    items = tracker.list(profile_id=profile_id, status=status)
    return {"items": items}

@router.post("/tracker", response_model=TrackerItem)
async def upsert_tracker(item: TrackerItem):
    return tracker.upsert(item)

@router.get("/tracker/export")
async def export_tracker(format: str = "csv", profile_id: Optional[str] = None, status: Optional[str] = None):
    items = tracker.list(profile_id=profile_id, status=status)
    if format == "csv":
        data = tracker.export_csv(items)
        return StreamingResponse(io.BytesIO(data), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=tracker.csv"})
    elif format == "xlsx":
        raise HTTPException(status_code=501, detail="xlsx not implemented yet")
    else:
        raise HTTPException(status_code=400, detail="Invalid format")
