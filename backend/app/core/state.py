from app.models.schemas import Job, Profile

_profiles: dict[str, Profile] = {}
_jobs: dict[str, Job] = {}


def store_profile(profile: Profile) -> None:
    _profiles[profile.id] = profile


def get_profile(profile_id: str) -> Profile | None:
    return _profiles.get(profile_id)


def store_jobs(jobs: list[Job]) -> None:
    for job in jobs:
        _jobs[job.id] = job


def get_job(job_id: str) -> Job | None:
    return _jobs.get(job_id)


def list_jobs() -> list[Job]:
    return list(_jobs.values())


def clear_state() -> None:
    _profiles.clear()
    _jobs.clear()
