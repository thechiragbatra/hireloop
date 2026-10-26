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


def _add_methods2():
    def save_jobs(self, jobs):
        return jobs
    Storage.save_jobs = save_jobs


_add_methods2()


def _add_methods3():
    def get_profile(self, profile_id, user_id=None):
        return None
    Storage.get_profile = get_profile


_add_methods3()


def _add_methods4():
    def create_all(self):
        pass
    Storage.create_all = create_all


_add_methods4()


# Override with proper implementation
class Storage:
    def __init__(self, database_url: str | None = None):
        from app.core.config import get_settings

        self.settings = get_settings()
        self.url = database_url or getattr(self.settings, "database_url", "sqlite:///./data/hireloop.db")
        self.url_async = getattr(self.settings, "database_url_async", "") or self.url
        self._profiles = {}
        self._jobs = {}
        self._apps = {}

    def create_all(self):
        pass

    def clear(self):
        self._profiles = {}
        self._jobs = {}
        self._apps = {}

    def save_profile(self, profile_id, raw_text=None, profile_data=None, user_id=None):
        self._profiles[profile_id] = {"id": profile_id, "raw_text": raw_text, "data": profile_data}
        return self._profiles[profile_id]

    def get_profile(self, profile_id, user_id=None):
        return self._profiles.get(profile_id)

    def save_job(self, job_id, job_data):
        self._jobs[job_id] = job_data
        return self._jobs[job_id]

    def save_jobs(self, jobs):
        for j in jobs:
            jid = j.get("id") if isinstance(j, dict) else getattr(j, "id", None)
            if jid:
                self._jobs[jid] = j
        return jobs

    def get_job(self, job_id):
        return self._jobs.get(job_id)

    def list_jobs(self):
        return list(self._jobs.values())

    def save_application(self, record, user_id=None):
        rid = record.get("id") if isinstance(record, dict) else getattr(record, "id", None)
        if rid:
            self._apps[rid] = record if isinstance(record, dict) else record.model_dump()
        return self._apps.get(rid)

    def list_applications(self, user_id=None, status=None):
        items = list(self._apps.values())
        if status:
            items = [i for i in items if i.get("status") == status]
        return items

    def get_application(self, record_id, user_id=None):
        return self._apps.get(record_id)
