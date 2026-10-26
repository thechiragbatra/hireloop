import io

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ...models.schemas import ApplicationRecord
from ...services.tracker import TrackerService

router = APIRouter()
tracker = TrackerService()


@router.get("/tracker")
async def list_tracker(profile_id: str | None = None, status: str | None = None):
    items = tracker.list(profile_id=profile_id, status=status)
    return {"items": [i.model_dump() for i in items]}


@router.post("/tracker")
async def upsert_tracker(item: ApplicationRecord):
    return tracker.upsert(item).model_dump()


@router.get("/tracker/export")
async def export_tracker(format: str = "csv", profile_id: str | None = None, status: str | None = None):
    items = tracker.list(profile_id=profile_id, status=status)
    if format == "csv":
        data = tracker.export_csv(items)
        return StreamingResponse(io.BytesIO(data), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=tracker.csv"})
    raise HTTPException(status_code=400, detail="Invalid format")
