import builtins
import csv
import io
from datetime import datetime

from ..models.schemas import TrackerItem


class TrackerService:
    def __init__(self):
        self._store = {}

    def upsert(self, item: TrackerItem) -> TrackerItem:
        item.date_updated = datetime.utcnow()
        self._store[item.tracker_id] = item
        return item

    def list(self, profile_id: str | None = None, status: str | None = None) -> list[TrackerItem]:
        items = list(self._store.values())
        if profile_id:
            items = [i for i in items if i.profile_id == profile_id]
        if status:
            items = [i for i in items if i.status == status]
        return items

    def export_csv(self, items: builtins.list[TrackerItem]) -> bytes:
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(
            [
                "tracker_id",
                "profile_id",
                "job_id",
                "company",
                "role",
                "link",
                "match_score",
                "status",
                "date_saved",
                "date_updated",
            ]
        )
        for i in items:
            w.writerow(
                [
                    i.tracker_id,
                    i.profile_id,
                    i.job_id,
                    i.company,
                    i.role,
                    i.link,
                    i.match_score,
                    i.status,
                    i.date_saved.isoformat(),
                    i.date_updated.isoformat(),
                ]
            )
        return buf.getvalue().encode("utf-8")
