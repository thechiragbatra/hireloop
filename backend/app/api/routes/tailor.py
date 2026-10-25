from fastapi import APIRouter

router = APIRouter()


@router.post("/tailor")
async def tailor():
    return {"status": "not_implemented"}
