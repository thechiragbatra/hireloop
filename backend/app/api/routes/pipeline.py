from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.auth import get_current_user
from app.core.config import get_settings
from app.core.storage import get_storage
from app.core.storage_files import get_storage_client
from app.graph import build_graph

router = APIRouter()
storage = get_storage()
storage_client = get_storage_client()
graph = build_graph()


@router.post("/pipeline")
async def pipeline(file: UploadFile = File(...), user: dict = Depends(get_current_user)) -> dict:
    """Run the full Hireloop pipeline: parse → fetch jobs → match → retrieve context → tailor → verify."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
    max_bytes = get_settings().max_upload_mb * 1024 * 1024
    content = await file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail="File too large")
    user_id = user["sub"]

    try:
        await storage_client.upload_resume(content, file.filename, user_id or "anonymous")
    except Exception:
        pass

    try:
        final_state = await graph.ainvoke(
            {
                "content": content,
                "filename": file.filename,
                "status": "started",
                "user_id": user_id,
            }
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {
        "profile_id": final_state.get("profile_id"),
        "status": final_state.get("status"),
        "jobs_count": len(final_state.get("jobs") or []),
        "matches": final_state.get("matches") or [],
        "tailored": final_state.get("tailored"),
        "faithfulness": final_state.get("faithfulness"),
        "user_id": user_id,
    }
