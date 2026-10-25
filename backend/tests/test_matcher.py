import anyio

from app.llm.client import FakeLLMClient
from app.models.schemas import Job, MatchResult, Profile
from app.services.matcher import Matcher


def test_match_returns_one_result_per_job():
    profile = Profile(id="p1", skills=["Python"])
    jobs = [
        Job(id="j1", title="Backend", company="Acme", description="d", source="greenhouse"),
        Job(id="j2", title="Frontend", company="Beta", description="d", source="lever"),
    ]
    matcher = Matcher(FakeLLMClient())
    results = anyio.run(matcher.match, profile, jobs)
    assert len(results) == 2
    assert {r.job_id for r in results} == {"j1", "j2"}
    for r in results:
        assert isinstance(r, MatchResult)
        assert 0.0 <= r.score <= 100
        assert isinstance(r.reasons, list)
        assert isinstance(r.missing_skills, list)
