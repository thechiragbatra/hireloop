import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SupabaseStorage:
    """Supabase Storage client: private bucket, signed URLs only."""

    def __init__(self):
        self.url = settings.supabase_url.rstrip("/") if settings.supabase_url else ""
        self.service_role_key = settings.supabase_service_role_key
        self.bucket = settings.supabase_storage_bucket
        self._client = httpx.AsyncClient(timeout=30)

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {
            "Authorization": f"Bearer {self.service_role_key}",
            "apikey": settings.supabase_anon_key,
        }
        return headers

    async def upload_resume(
        self,
        file_content: bytes,
        filename: str,
        user_id: str,
        content_type: str = "application/octet-stream",
    ) -> dict[str, Any]:
        """Upload a resume to a private bucket under the user's folder."""
        path = f"{user_id}/resumes/{filename}"
        try:
            resp = await self._client.post(
                f"{self.url}/storage/v1/object/{self.bucket}/{path}",
                headers={**self._headers(), "Content-Type": content_type, "x-upsert": "true"},
                content=file_content,
            )
            resp.raise_for_status()
            return {
                "bucket": self.bucket,
                "path": path,
                "size": len(file_content),
                "user_id": user_id,
            }
        except Exception as exc:  # noqa: BLE001
            logger.error("Supabase Storage upload failed", extra={"error": str(exc)[:200]})
            raise

    async def upload_cover_letter(
        self,
        file_content: bytes,
        filename: str,
        user_id: str,
        content_type: str = "application/pdf",
    ) -> dict[str, Any]:
        """Upload a cover letter PDF to a private bucket."""
        path = f"{user_id}/cover-letters/{filename}"
        try:
            resp = await self._client.post(
                f"{self.url}/storage/v1/object/{self.bucket}/{path}",
                headers={**self._headers(), "Content-Type": content_type, "x-upsert": "true"},
                content=file_content,
            )
            resp.raise_for_status()
            return {
                "bucket": self.bucket,
                "path": path,
                "size": len(file_content),
                "user_id": user_id,
            }
        except Exception as exc:  # noqa: BLE001
            logger.error("Supabase Storage upload failed", extra={"error": str(exc)[:200]})
            raise

    async def get_signed_url(self, path: str, expires_in: int = 3600) -> str:
        """Generate a signed URL for private object access."""
        try:
            resp = await self._client.post(
                f"{self.url}/storage/v1/object/sign",
                headers=self._headers(),
                json={"path": path, "expires_in": expires_in},
            )
            resp.raise_for_status()
            data = resp.json()
            signed_path = data.get("signedURL", "")
            return f"{self.url}{signed_path}"
        except Exception as exc:  # noqa: BLE001
            logger.error("Supabase Storage signed URL failed", extra={"error": str(exc)[:200]})
            raise

    async def delete_file(self, path: str) -> bool:
        """Delete a file from the private bucket."""
        try:
            resp = await self._client.delete(
                f"{self.url}/storage/v1/object/{self.bucket}/{path}",
                headers=self._headers(),
            )
            return resp.status_code in (200, 204)
        except Exception:
            return False

    async def aclose(self) -> None:
        await self._client.aclose()


_storage_client: SupabaseStorage | None = None


def get_storage_client() -> SupabaseStorage:
    global _storage_client
    if _storage_client is None:
        _storage_client = SupabaseStorage()
    return _storage_client
