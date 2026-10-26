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
