from typing import List, Optional

from ..models.schemas import ApplicationRecord


class TrackerService:
    def __init__(self):
        self._store = {}

    def upsert(self, item: ApplicationRecord) -> ApplicationRecord:
        self._store[item.id] = item
        return item

    def list(self, profile_id: Optional[str] = None, status: Optional[str] = None) -> List[ApplicationRecord]:
        items = list(self._store.values())
        if status:
            items = [i for i in items if i.status == status]
        return items

    def export_csv(self, items: List[ApplicationRecord]) -> bytes:
        import csv
        import io

        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["id", "company", "role", "url", "match_score", "status", "date", "resume_version"])
        for i in items:
            w.writerow([i.id, i.company, i.role, i.url, i.match_score, i.status, i.date.isoformat(), i.resume_version])
        return buf.getvalue().encode("utf-8")
