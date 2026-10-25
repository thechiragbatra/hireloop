from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.storage import get_storage
from app.graph import build_graph

router = APIRouter()
storage = get_storage()
graph = build_graph()


@router.post("/pipeline")
async def pipeline(file: UploadFile = File(...)) -> dict:
    """Run the full Hireloop pipeline: parse → fetch jobs → match → retrieve context → tailor → verify."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    content = await file.read()
    try:
        final_state = await graph.ainvoke(
            {"content": content, "filename": file.filename, "status": "started"}
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
    }
