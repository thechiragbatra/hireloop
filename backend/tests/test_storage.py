from datetime import datetime

from app.core.storage import Storage
from app.models.schemas import ApplicationRecord, Job, Profile


def _fresh_storage():

    return Storage(database_url="sqlite:///:memory:")


def test_storage_profile_round_trip():
    storage = _fresh_storage()
    profile = Profile(id="p1", skills=["Python"])
    storage.save_profile(profile.id, "raw text", profile.model_dump())
    got = storage.get_profile(profile.id)
    assert got is not None
    assert got["id"] == "p1"
    assert got["data"]["skills"] == ["Python"]
    assert storage.get_profile("missing") is None


def test_storage_jobs_round_trip():
    storage = _fresh_storage()
    jobs = [
        Job(id="j1", title="Backend", company="Acme", description="d", source="greenhouse"),
        Job(id="j2", title="Frontend", company="Beta", description="d", source="lever"),
    ]
    storage.save_jobs([j.model_dump() for j in jobs])
    assert len(storage.list_jobs()) == 2
    assert storage.get_job("j1") is not None
    assert storage.get_job("j1")["id"] == "j1"
    assert storage.get_job("missing") is None


def test_storage_applications_crud():
    storage = _fresh_storage()
    record = ApplicationRecord(
        id="r1",
        company="Acme",
        role="Eng",
        match_score=80.0,
        resume_version="v1",
        date=datetime(2026, 1, 1),
    )
    storage.save_application(record.model_dump())
    got = storage.get_application("r1")
    assert got is not None
    assert got["company"] == "Acme"
    assert got["status"] == "saved"
    assert storage.get_application("missing") is None

    # update status
    record.status = "applied"
    storage.save_application(record.model_dump())
    assert storage.get_application("r1")["status"] == "applied"

    # list + filter
    assert len(storage.list_applications()) == 1
    assert len(storage.list_applications(status="applied")) == 1
    assert len(storage.list_applications(status="saved")) == 0

    # delete
    assert storage.delete_application("r1") is True
    assert storage.delete_application("r1") is False
    assert storage.list_applications() == []


def test_storage_clear():
    storage = _fresh_storage()
    storage.save_profile("p1", "t", Profile(id="p1").model_dump())
    storage.save_jobs(
        [Job(id="j1", title="B", company="C", description="d", source="greenhouse").model_dump()]
    )
    storage.clear()
    assert storage.get_profile("p1") is None
    assert storage.list_jobs() == []
