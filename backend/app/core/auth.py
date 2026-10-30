from functools import lru_cache
from typing import Any, cast

import jwt
from fastapi import HTTPException, Request
from jwt import PyJWKClient

from app.core.config import get_settings


@lru_cache(maxsize=4)
def _jwks_client(url: str) -> PyJWKClient:
    return PyJWKClient(url, cache_keys=True)


def get_current_user(request: Request) -> dict:
    """Verify Supabase access tokens. Unauthenticated local mode is dev-only."""
    settings = get_settings()
    header = request.headers.get("authorization", "")
    if not header:
        if settings.app_env.lower() not in {"production", "prod"}:
            return {"sub": "local", "email": "local@hireloop.dev"}
        raise HTTPException(status_code=401, detail="Sign in to continue")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    try:
        issuer = (settings.supabase_url.rstrip("/") + "/auth/v1") if settings.supabase_url else None
        if settings.supabase_jwt_secret:
            try:
                claims = jwt.decode(
                    token,
                    settings.supabase_jwt_secret,
                    algorithms=["HS256"],
                    audience="authenticated",
                    issuer=issuer,
                )
            except jwt.InvalidTokenError:
                if not (settings.supabase_jwks_url or settings.supabase_url):
                    raise
                claims = None
        else:
            claims = None
        if claims is None and (settings.supabase_jwks_url or settings.supabase_url):
            jwks_url = settings.supabase_jwks_url or (
                settings.supabase_url.rstrip("/") + "/auth/v1/.well-known/jwks.json"
            )
            signing_key = _jwks_client(jwks_url).get_signing_key_from_jwt(token).key
            options = cast(Any, {"verify_aud": bool(settings.supabase_url)})
            claims = jwt.decode(
                token,
                signing_key,
                algorithms=["ES256", "RS256"],
                audience="authenticated" if settings.supabase_url else None,
                options=options,
                issuer=issuer,
            )
        elif claims is None:
            raise HTTPException(status_code=503, detail="Authentication is not configured")
        if not claims.get("sub"):
            raise jwt.InvalidTokenError("Missing subject")
        return claims
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired access token") from exc
