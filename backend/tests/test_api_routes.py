import io

from docx import Document
from fastapi.testclient import TestClient

from app.core.storage import get_storage
from app.models.schemas import ApplicationRecord, Bullet, ExperienceItem, Job, Profile, ProjectItem

storage = get_storage()


def _make_docx(text: str) -> bytes:
    doc = Document()
    doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _save_profile(profile: Profile, raw_text: str = ""):
    storage.save_profile(profile.id, raw_text, profile.model_dump())


def _save_job(job: Job):
    storage.save_jobs([job.model_dump()])


def test_health(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_docx(client: TestClient):
    content = _make_docx("Hello World")
    response = client.post(
        "/api/v1/upload",
        files={
            "file": (
                "resume.docx",
                content,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["raw_text"] == "Hello World"
    assert body["profile"]["id"]
    assert body["profile"]["skills"] == []


def test_upload_unsupported_type(client: TestClient):
    response = client.post(
        "/api/v1/upload",
        files={"file": ("resume.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


def test_jobs_fetch(client: TestClient):
    response = client.get("/api/v1/jobs")
    assert response.status_code == 200
    assert response.json() == {"jobs": []}


def test_match_requires_profile(client: TestClient):
    response = client.post(
        "/api/v1/match",
        json={"profile_id": "missing", "jobs": []},
    )
    assert response.status_code == 404


def test_match_returns_structured_results(client: TestClient):
    _save_profile(Profile(id="p1", skills=["Python"]))
    job = Job(id="j1", title="Backend", company="Acme", description="d", source="greenhouse")
    _save_job(job)
    response = client.post("/api/v1/match", json={"profile_id": "p1", "jobs": []})
    assert response.status_code == 200, response.text
    body = response.json()
    assert len(body["matches"]) == 1
    assert body["matches"][0]["job_id"] == "j1"
    assert 0.0 <= body["matches"][0]["score"] <= 100


def test_tailor_requires_profile_and_job(client: TestClient):
    response = client.post("/api/v1/tailor?profile_id=missing&job_id=j1")
    assert response.status_code == 404


def test_tailor_returns_tailored_resume(client: TestClient):
    _save_profile(
        Profile(
            id="p1",
            skills=["Python"],
            experience=[
                ExperienceItem(
                    id="e1",
                    company="Acme",
                    title="Engineer",
                    bullets=[Bullet(id="e1b1", text="Built APIs")],
                )
            ],
            projects=[
                ProjectItem(
                    id="pr1",
                    name="Demo",
                    bullets=[Bullet(id="pr1b1", text="Wrote code")],
                    technologies=["Python"],
                )
            ],
        )
    )
    _save_job(Job(id="j1", title="Backend", company="Acme", description="d", source="greenhouse"))
    response = client.post("/api/v1/tailor?profile_id=p1&job_id=j1")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["job_id"] == "j1"
    assert len(body["bullets"]) == 3


def test_tracker_crud(client: TestClient):
    # create
    payload = {
        "id": "r1",
        "company": "Acme",
        "role": "Eng",
        "match_score": 80.0,
        "resume_version": "v1",
    }
    response = client.post("/api/v1/tracker", json=payload)
    assert response.status_code == 200
    assert response.json()["company"] == "Acme"

    # list
    response = client.get("/api/v1/tracker")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1

    # get
    response = client.get("/api/v1/tracker/r1")
    assert response.status_code == 200
    assert response.json()["role"] == "Eng"

    # update
    response = client.put(
        "/api/v1/tracker/r1",
        json={**payload, "status": "applied"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "applied"

    # delete
    response = client.delete("/api/v1/tracker/r1")
    assert response.status_code == 200
    assert response.json()["deleted"] == "r1"
    response = client.get("/api/v1/tracker/r1")
    assert response.status_code == 404


def test_tracker_create_record_model():
    # ensure the schema itself validates
    r = ApplicationRecord(
        id="r1", company="Acme", role="Eng", match_score=80.0, resume_version="v1"
    )
    assert r.status == "saved"
