import anyio

from app.models.schemas import (
    Bullet,
    ExperienceItem,
    Job,
    Profile,
    ProjectItem,
    TailoredResume,
)
from app.services.tailor import TailorService


def _profile():
    return Profile(
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


def test_tailor_fallback_returns_tailored_resume():
    job = Job(id="j1", title="Backend", company="Acme", description="d", source="greenhouse")
    result = anyio.run(TailorService().tailor, _profile(), job)
    assert isinstance(result, TailoredResume)
    assert result.job_id == "j1"
    assert len(result.bullets) == 3
    assert all(b.source_ids for b in result.bullets)
