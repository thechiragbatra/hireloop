import anyio

from app.models.schemas import Job, Profile
from app.services.matcher import Matcher


def test_matcher_fallback_returns_one_result_per_job():
    profile = Profile(id="p1", skills=["Python"])
    jobs = [
        Job(id="j1", title="Backend", company="Acme", description="d", source="greenhouse"),
        Job(id="j2", title="Frontend", company="Beta", description="d", source="lever"),
    ]
    results = anyio.run(Matcher().match, profile, jobs)
    assert len(results) == 2
    assert {r.job_id for r in results} == {"j1", "j2"}
    for r in results:
        assert r.score == 0.0
        assert r.reasons == ["LLM not configured"]
        assert r.missing_skills == []
