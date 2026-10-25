from datetime import datetime

from app.models.schemas import ApplicationRecord
from app.services.tracker import TrackerService


def test_tracker_upsert_and_list():
    service = TrackerService()
    r = ApplicationRecord(id="1", company="Acme", role="Eng", match_score=80.0, resume_version="v1")
    created = service.upsert(r)
    assert created.id == "1"
    items = service.list()
    assert len(items) == 1
    assert items[0].company == "Acme"


def test_tracker_list_filter_by_status():
    service = TrackerService()
    service.upsert(
        ApplicationRecord(
            id="1", company="A", role="R", match_score=1.0, resume_version="v1", status="applied"
        )
    )
    service.upsert(
        ApplicationRecord(
            id="2", company="B", role="R", match_score=2.0, resume_version="v1", status="saved"
        )
    )
    applied = service.list(status="applied")
    assert len(applied) == 1
    assert applied[0].id == "1"


def test_tracker_delete():
    service = TrackerService()
    service.upsert(
        ApplicationRecord(id="1", company="A", role="R", match_score=1.0, resume_version="v1")
    )
    assert service.delete("1") is True
    assert service.delete("1") is False
    assert service.list() == []


def test_tracker_export_csv():
    service = TrackerService()
    service.upsert(
        ApplicationRecord(
            id="1",
            company="Acme",
            role="Eng",
            match_score=80.0,
            resume_version="v1",
            date=datetime(2026, 1, 1),
        )
    )
    csv_bytes = service.export_csv(service.list())
    text = csv_bytes.decode("utf-8")
    assert "Acme" in text
    assert "Eng" in text
    assert "2026-01-01T00:00:00" in text
