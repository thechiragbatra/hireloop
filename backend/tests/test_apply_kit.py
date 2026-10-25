from fastapi.testclient import TestClient


def test_apply_kit_requires_profile_and_job(client: TestClient):
    response = client.get("/api/v1/apply-kit/missing/j1")
    assert response.status_code == 404

    response = client.get("/api/v1/apply-kit/p1/missing")
    assert response.status_code == 404


def test_apply_kit_returns_kit(client: TestClient):
    from app.core.storage import get_storage
    from app.models.schemas import Job, Profile

    storage = get_storage()
    storage.save_profile("p1", "raw", Profile(id="p1", skills=["Python"]).model_dump())
    storage.save_jobs(
        [
            Job(
                id="j1",
                title="Backend",
                company="Acme",
                description="We need Python",
                source="greenhouse",
            ).model_dump()
        ]
    )

    response = client.get("/api/v1/apply-kit/p1/j1")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["job_id"] == "j1"
    assert body["profile_id"] == "p1"
    assert body["tailored_resume"]["job_id"] == "j1"
    assert "note" in body
    assert "No auto-submit" in body["note"]
