import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from ...core.auth import get_current_user
from ...models.schemas import ApplicationRecord
from ...services.tracker import TrackerService

router = APIRouter()
tracker = TrackerService()


@router.get("/tracker")
async def list_tracker(
    profile_id: str | None = None, status: str | None = None, user: dict = Depends(get_current_user)
):
    items = tracker.list(profile_id=profile_id, status=status, user_id=user["sub"])
    return {"items": [i.model_dump() for i in items]}


@router.post("/tracker")
async def upsert_tracker(item: ApplicationRecord, user: dict = Depends(get_current_user)):
    return tracker.upsert(item, user_id=user["sub"]).model_dump(mode="json")


@router.get("/tracker/export")
async def export_tracker(
    format: str = "csv",
    profile_id: str | None = None,
    status: str | None = None,
    user: dict = Depends(get_current_user),
):
    items = tracker.list(profile_id=profile_id, status=status, user_id=user["sub"])
    if format != "csv":
        raise HTTPException(status_code=400, detail="Invalid format")
    data = tracker.export_csv(items)
    return StreamingResponse(
        io.BytesIO(data),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=applications.csv"},
    )


@router.get("/tracker/{record_id}")
async def get_tracker_item(record_id: str, user: dict = Depends(get_current_user)):
    item = tracker.get(record_id, user_id=user["sub"])
    if not item:
        raise HTTPException(status_code=404, detail="Application not found")
    return item.model_dump(mode="json")


@router.put("/tracker/{record_id}")
async def update_tracker_item(
    record_id: str, item: ApplicationRecord, user: dict = Depends(get_current_user)
):
    if record_id != item.id or not tracker.get(record_id, user_id=user["sub"]):
        raise HTTPException(status_code=404, detail="Application not found")
    return tracker.upsert(item, user_id=user["sub"]).model_dump(mode="json")


@router.delete("/tracker/{record_id}")
async def delete_tracker_item(record_id: str, user: dict = Depends(get_current_user)):
    if not tracker.delete(record_id, user_id=user["sub"]):
        raise HTTPException(status_code=404, detail="Application not found")
    return {"deleted": record_id}
