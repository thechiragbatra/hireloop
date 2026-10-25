from fastapi.testclient import TestClient


def test_pipeline_upload_unsupported_type(client: TestClient):
    response = client.post(
        "/api/v1/pipeline",
        files={"file": ("resume.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


def test_pipeline_docx(client: TestClient):
    import io

    from docx import Document

    doc = Document()
    doc.add_paragraph("Built APIs with Python and FastAPI")
    buf = io.BytesIO()
    doc.save(buf)
    content = buf.getvalue()

    response = client.post(
        "/api/v1/pipeline",
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
    assert body["profile_id"]
    assert body["status"] in ("verified", "tailored", "nothing_to_verify")
    assert isinstance(body["matches"], list)
    if body["jobs_count"] == 0:
        assert body["tailored"] is None
