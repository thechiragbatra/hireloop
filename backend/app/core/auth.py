
from fastapi import Request


def get_current_user(request: Request) -> dict | None:
    # Dev mode - no auth required
    return None
