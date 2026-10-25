from app.core.config import get_settings


def test_settings_load():
    settings = get_settings()
    assert settings.app_env == "development"
    assert settings.log_resume_text is False
