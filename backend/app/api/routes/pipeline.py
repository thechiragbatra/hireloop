from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.auth import get_current_user
from app.core.storage import get_storage
from app.core.storage_files import get_storage_client
from app.graph import build_graph

router = APIRouter()
storage = get_storage()
storage_client = get_storage_client()
graph = build_graph()


@router.post("/pipeline")
async def pipeline(
    file: UploadFile = File(...),
    user: dict | None = Depends(get_current_user),
) -> dict:
    """Run the full Hireloop pipeline: parse → fetch jobs → match → retrieve context → tailor → verify."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    content = await file.read()
    user_id = user.get("sub") if user else None

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
    return {
        "profile_id": final_state.get("profile_id"),
        "status": final_state.get("status"),
        "jobs_count": len(final_state.get("jobs") or []),
        "matches": final_state.get("matches") or [],
        "tailored": final_state.get("tailored"),
        "faithfulness": final_state.get("faithfulness"),
        "user_id": user_id,
    }
