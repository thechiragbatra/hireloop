from typing import Any, cast

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings

settings = get_settings()

bearer_scheme = HTTPBearer(auto_error=False)

_jwks_client: jwt.PyJWKClient | None = None


def _get_jwks_client() -> jwt.PyJWKClient | None:
    global _jwks_client
    if _jwks_client is not None:
        return _jwks_client
    if not settings.supabase_url:
        return None
    jwks_uri = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
    try:
        _jwks_client = jwt.PyJWKClient(jwks_uri)
    except Exception:
        _jwks_client = None
    return _jwks_client


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any] | None:
    """Verify Supabase JWT via JWKS and return user payload, or None if auth not required."""
    if not settings.supabase_url or not settings.supabase_jwt_secret:
        # Auth not configured; allow unauthenticated access (dev only)
        return None
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        jwks_client = _get_jwks_client()
        if jwks_client is None:
            # Fallback to symmetric secret verification
            payload = jwt.decode(
                credentials.credentials,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
                issuer=f"{settings.supabase_url}/auth/v1",
            )
        else:
            signing_key = cast(
                str, jwks_client.get_signing_key_from_jwt(credentials.credentials).key
            )
            payload = jwt.decode(
                credentials.credentials,
                signing_key,
                algorithms=["RS256"],
                audience="authenticated",
                issuer=f"{settings.supabase_url}/auth/v1",
            )
        return cast(dict[str, Any], payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_auth(user: dict[str, Any] | None = Depends(get_current_user)) -> dict[str, Any]:
    """Dependency that requires a valid authenticated user."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return user


def get_user_id(user: dict[str, Any] | None = Depends(get_current_user)) -> str | None:
    """Extract the Supabase user ID (sub) from the JWT payload."""
    if user is None:
        return None
    return user.get("sub")
