from fastapi import Depends, HTTPException, Request
from typing import Optional


def get_current_user(request: Request) -> Optional[dict]:
    # Dev mode - no auth required
    return None
