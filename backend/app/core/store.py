
from ..models.schemas import Profile

_profiles: dict[str, Profile] = {}


def save_profile(profile: Profile) -> None:
    _profiles[profile.id] = profile


def get_profile(profile_id: str) -> Profile | None:
    return _profiles.get(profile_id)


def delete_profile(profile_id: str) -> None:
    _profiles.pop(profile_id, None)
