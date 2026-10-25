import anyio

from app.models.schemas import (
    Bullet,
    ExperienceItem,
    Profile,
    TailoredBullet,
    TailoredResume,
)
from app.services.faithfulness import FaithfulnessService


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
    )


def test_faithfulness_fallback_returns_full_score():
    tailored = TailoredResume(
        job_id="j1",
        bullets=[TailoredBullet(text="Built APIs", source_ids=["e1b1"])],
        summary=None,
    )
    report = anyio.run(FaithfulnessService().verify, _profile(), tailored)
    assert report.overall_score == 1.0
    assert report.supported_bullets == 1
    assert report.total_bullets == 1
    assert report.unsupported == []
