import builtins

from ..core.storage import get_storage
from ..models.schemas import ApplicationRecord


class TrackerService:
    def __init__(self):
        self.storage = get_storage()

    def upsert(self, item: ApplicationRecord, user_id: str | None = None) -> ApplicationRecord:
        self.storage.save_application(item.model_dump(mode="json"), user_id=user_id)
        return item

    def list(
        self,
        profile_id: str | None = None,
        status: str | None = None,
        user_id: str | None = None,
    ) -> list[ApplicationRecord]:
        rows = self.storage.list_applications(user_id=user_id, status=status)
        if profile_id:
            rows = [row for row in rows if row.get("profile_id") == profile_id]
        return [ApplicationRecord.model_validate(item) for item in rows]

    def export_csv(self, items: builtins.list[ApplicationRecord]) -> bytes:
        import csv
        import io

        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(
            ["id", "company", "role", "url", "match_score", "status", "date", "resume_version"]
        )
        for i in items:
            w.writerow(
                [
                    i.id,
                    i.company,
                    i.role,
                    i.url,
                    i.match_score,
                    i.status,
                    i.date.isoformat(),
                    i.resume_version,
                ]
            )
        return buf.getvalue().encode("utf-8")

    def get(self, record_id: str, user_id: str | None = None) -> ApplicationRecord | None:
        item = self.storage.get_application(record_id, user_id=user_id)
        return ApplicationRecord.model_validate(item) if item else None

    def delete(self, record_id: str, user_id: str | None = None) -> bool:
        return bool(self.storage.delete_application(record_id, user_id=user_id))

    def clear(self) -> None:
        self.storage.clear()
