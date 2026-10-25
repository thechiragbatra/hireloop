from fastapi import APIRouter

router = APIRouter()


@router.get("/jobs")
async def jobs():
    return {"jobs": []}
