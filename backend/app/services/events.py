import json
from typing import AsyncIterator

from ..schemas.events import RunEvent


class EventStore:
    def __init__(self):
        self._events: dict[str, list[RunEvent]] = {}

    def emit(self, event: RunEvent) -> None:
        if event.run_id not in self._events:
            self._events[event.run_id] = []
        self._events[event.run_id].append(event)

    def get_events(self, run_id: str) -> list[RunEvent]:
        return self._events.get(run_id, [])

    async def stream(self, run_id: str) -> AsyncIterator[str]:
        # Replay existing events
        for ev in self.get_events(run_id):
            yield f"data: {ev.model_dump_json()}\n\n"
        # In production, would wait for new events
        yield "event: done\ndata: {}\n\n"


event_store = EventStore()
