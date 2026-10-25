import anyio

from app.services.job_sources import ADAPTERS


def test_adapters_return_empty():
    for name, adapter in ADAPTERS.items():
        jobs = anyio.run(adapter.fetch, {})
        assert jobs == []
    assert set(ADAPTERS) == {"greenhouse", "lever", "ashby", "adzuna", "remoteok", "custom"}
