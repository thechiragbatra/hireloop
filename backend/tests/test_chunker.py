from app.models.schemas import Bullet, ExperienceItem, Profile, ProjectItem
from app.services.chunker import ProfileChunker


def test_chunker_experience_and_projects_and_skills():
    profile = Profile(
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
    )
    chunks = ProfileChunker().chunk(profile)
    assert len(chunks) == 3
    sources = {c["source"] for c in chunks}
    assert sources == {"experience", "project", "skill"}
    assert chunks[0]["id"] == "e1b1"
    assert chunks[0]["text"] == "Built APIs"
    assert chunks[2]["id"] == "skills"


def test_chunker_empty_profile():
    chunks = ProfileChunker().chunk(Profile(id="p1"))
    assert chunks == []
