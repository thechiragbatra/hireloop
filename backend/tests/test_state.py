from app.core.state import (
    clear_state,
    get_job,
    get_profile,
    list_jobs,
    store_jobs,
    store_profile,
)
from app.models.schemas import Job, Profile


def test_state_profile_round_trip():
    clear_state()
    profile = Profile(id="p1", skills=["Python"])
    store_profile(profile)
    assert get_profile("p1") is profile
    assert get_profile("missing") is None


def test_state_jobs_round_trip():
    clear_state()
    jobs = [
        Job(id="j1", title="Backend", company="Acme", description="d", source="greenhouse"),
        Job(id="j2", title="Frontend", company="Beta", description="d", source="lever"),
    ]
    store_jobs(jobs)
    assert list_jobs() == jobs
    assert get_job("j1") is jobs[0]
    assert get_job("missing") is None


def test_state_clear():
    clear_state()
    store_profile(Profile(id="p1"))
    store_jobs([Job(id="j1", title="B", company="C", description="d", source="greenhouse")])
    clear_state()
    assert get_profile("p1") is None
    assert list_jobs() == []
