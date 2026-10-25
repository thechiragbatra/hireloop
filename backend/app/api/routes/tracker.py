from fastapi import APIRouter

router = APIRouter()


@router.get("/tracker")
async def tracker():
    return {"items": []}
