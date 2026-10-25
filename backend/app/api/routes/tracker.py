from fastapi import APIRouter, HTTPException

from app.core.storage import get_storage
from app.models.schemas import ApplicationRecord

router = APIRouter()
storage = get_storage()


@router.get("/tracker")
async def list_records(status: str | None = None) -> dict:
    items = storage.list_applications(status=status)
    return {"items": items}


@router.post("/tracker")
async def create_record(record: ApplicationRecord) -> dict:
    storage.save_application(record.model_dump())
    return record.model_dump()


@router.get("/tracker/{record_id}")
async def get_record(record_id: str) -> dict:
    record = storage.get_application(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.put("/tracker/{record_id}")
async def update_record(record_id: str, record: ApplicationRecord) -> dict:
    if record.id != record_id:
        record.id = record_id
    storage.save_application(record.model_dump())
    return record.model_dump()


@router.delete("/tracker/{record_id}")
async def delete_record(record_id: str) -> dict:
    deleted = storage.delete_application(record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"deleted": record_id}
