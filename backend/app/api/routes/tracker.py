from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_current_user
from app.core.storage import get_storage
from app.models.schemas import ApplicationRecord

router = APIRouter()
storage = get_storage()


@router.get("/tracker")
async def list_records(
    status: str | None = None,
    user: dict | None = Depends(get_current_user),
) -> dict:
    user_id = user.get("sub") if user else None
    items = storage.list_applications(user_id=user_id, status=status)
    return {"items": items}


@router.post("/tracker")
async def create_record(
    record: ApplicationRecord,
    user: dict | None = Depends(get_current_user),
) -> dict:
    user_id = user.get("sub") if user else None
    storage.save_application(record.model_dump(), user_id=user_id)
    return record.model_dump()


@router.get("/tracker/{record_id}")
async def get_record(
    record_id: str,
    user: dict | None = Depends(get_current_user),
) -> dict:
    user_id = user.get("sub") if user else None
    record = storage.get_application(record_id, user_id=user_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.put("/tracker/{record_id}")
async def update_record(
    record_id: str,
    record: ApplicationRecord,
    user: dict | None = Depends(get_current_user),
) -> dict:
    user_id = user.get("sub") if user else None
    if record.id != record_id:
        record.id = record_id
    storage.save_application(record.model_dump(), user_id=user_id)
    return record.model_dump()


@router.delete("/tracker/{record_id}")
async def delete_record(
    record_id: str,
    user: dict | None = Depends(get_current_user),
) -> dict:
    user_id = user.get("sub") if user else None
    deleted = storage.delete_application(record_id, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"deleted": record_id}


@router.delete("/account")
async def delete_account(
    user: dict | None = Depends(get_current_user),
) -> dict:
    """Delete all user data (GDPR / 'delete my account')."""
    user_id = user.get("sub") if user else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    storage.delete_user_data(user_id)
    return {"deleted": user_id}
