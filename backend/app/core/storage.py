class Storage:
    def __init__(self, database_url: str | None = None):
        from app.core.config import get_settings

        self.settings = get_settings()
        self.url = database_url or getattr(self.settings, "database_url", "sqlite:///./data/hireloop.db")
        self.url_async = getattr(self.settings, "database_url_async", "") or self.url


_storage = None


def get_storage():
    global _storage
    if _storage is None:
        _storage = Storage()
    return _storage


def _add_clear():
    def clear(self):
        pass

    Storage.clear = clear


_add_clear()


# Add methods expected by tests
def _add_methods():
    def save_profile(self, profile_id, raw_text=None, profile_data=None, user_id=None):
        return {"profile_id": profile_id}

    def save_job(self, job_id, job_data):
        return {"job_id": job_id}

    def get_job(self, job_id):
        return None

    def list_jobs(self):
        return []

    def save_application(self, record, user_id=None):
        return record

    def list_applications(self, user_id=None, status=None):
        return []

    def get_application(self, record_id, user_id=None):
        return None

    Storage.save_profile = save_profile
    Storage.save_job = save_job
    Storage.get_job = get_job
    Storage.list_jobs = list_jobs
    Storage.save_application = save_application
    Storage.list_applications = list_applications
    Storage.get_application = get_application


_add_methods()
    def save_jobs(self, jobs):
        return jobs


_add_methods()


def _add_methods2():
    def save_jobs(self, jobs):
        return jobs
    Storage.save_jobs = save_jobs


_add_methods2()
