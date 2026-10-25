from app.models.schemas import ApplicationRecord


def test_application_record():
    r = ApplicationRecord(id="1", company="Acme", role="Eng", match_score=80.0, resume_version="v1")
    assert r.company == "Acme"
