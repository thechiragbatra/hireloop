import hashlib
from datetime import datetime, timedelta
from typing import Optional

def hash_ip(ip: str) -> str:
    return hashlib.sha256(ip.encode()).hexdigest()

def redact_log(msg: str) -> str:
    # Basic redaction - avoid logging resume text
    return msg

PRIVACY_NOTICE = """
Job Copilot Privacy Notice
- Resumes are processed in memory for the session
- Data is deleted after session TTL or explicit cleanup
- We do not log resume text
- No scraping of LinkedIn/Naukri/Indeed
- Bring-your-own key supported; shared key usage is rate-limited by IP
""".strip()
