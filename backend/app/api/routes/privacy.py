from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.core.storage import get_storage

router = APIRouter()
storage = get_storage()


@router.delete("/account/data")
async def delete_account_data(user: dict = Depends(get_current_user)):
    """Erase this user's stored profiles and application records."""
    deleted = storage.delete_user_data(user["sub"])
    return {"deleted_records": deleted}
