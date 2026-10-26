from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from ...core.auth import get_current_user
from ...services.events import event_store

router = APIRouter()


@router.get("/runs/{run_id}/events")
async def stream_events(run_id: str, user: dict | None = Depends(get_current_user)):
    async def event_generator():
        async for chunk in event_store.stream(run_id):
            yield chunk

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
