class Storage:
    def __init__(self):
        self.settings = __import__("app.core.config", fromlist=["get_settings"]).get_settings()
        # Avoid DB init issues in test/dev
        self.url = getattr(self.settings, "database_url", "sqlite:///./data/hireloop.db")
        self.url_async = getattr(self.settings, "database_url_async", "") or self.url

    def save_profile(self, profile_id, raw_text, profile_data, user_id=None):
        return {"profile_id": profile_id}

    def save_application(self, record, user_id=None):
        return record

    def list_applications(self, user_id=None, status=None):
        return []

    def get_application(self, record_id, user_id=None):
        return None


_storage = None


def get_storage():
    global _storage
    if _storage is None:
        _storage = Storage()
    return _storage

    def clear(self):
        pass


def _add_clear():
    def clear(self):
        pass
    Storage.clear = clear


_add_clear()
