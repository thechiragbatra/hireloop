from app.services.job_sources import ADAPTERS


def test_adapter_registry_uses_current_public_sources():
    assert set(ADAPTERS) == {
        "remoteok",
        "weworkremotely",
        "jobicy",
        "himalayas",
        "greenhouse",
        "lever",
        "ashby",
        "adzuna",
        "otta",
    }
    assert all(callable(adapter.fetch) for adapter in ADAPTERS.values())
