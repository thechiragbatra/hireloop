from datetime import datetime, timedelta
from typing import Dict, Tuple
from .privacy import hash_ip

# In-memory simple rate limiter (for dev; can be moved to Redis)
_store: Dict[Tuple[str, str], list[datetime]] = {}

def check_rate_limit(ip: str, endpoint: str, limit_per_min: int = 10) -> bool:
    key = (hash_ip(ip), endpoint)
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=1)
    # prune
    arr = _store.get(key, [])
    arr = [t for t in arr if t > window_start]
    if len(arr) >= limit_per_min:
        _store[key] = arr
        return False
    arr.append(now)
    _store[key] = arr
    return True
