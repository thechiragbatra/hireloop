from app.models.schemas import Profile


def test_profile_exists():
    p = Profile(id="x")
    assert p.id == "x"
