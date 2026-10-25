import pytest
from fastapi.testclient import TestClient

from app.core.storage import get_storage
from app.llm.client import FakeLLMClient
from app.main import app
from app.models.schemas import Bullet, ExperienceItem, Job, Profile, ProjectItem


@pytest.fixture(autouse=True)
def clean_storage():
    storage = get_storage()
    storage.clear()


@pytest.fixture
def sample_profile() -> Profile:
    return Profile(
        id="p1",
        skills=["Python", "FastAPI"],
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
        education=[],
    )


@pytest.fixture
def sample_job() -> Job:
    return Job(
        id="j1",
        title="Backend Engineer",
        company="TechCo",
        description="We need Python engineer",
        requirements=["Python", "FastAPI"],
        source="greenhouse",
    )


@pytest.fixture
def fake_llm() -> FakeLLMClient:
    return FakeLLMClient()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
