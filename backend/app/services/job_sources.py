from typing import Any

import httpx

from ..core.config import get_settings
from ..models.schemas import Job

settings = get_settings()


class JobSourceAdapter:
    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        raise NotImplementedError


def _to_job(
    source: str,
    job_id: str,
    title: str,
    company: str,
    description: str = "",
    location: str | None = None,
    url: str | None = None,
    requirements: list[str] | None = None,
) -> Job:
    return Job(
        id=f"{source}:{job_id}",
        title=title,
        company=company,
        location=location,
        description=description,
        requirements=requirements or [],
        url=url,
        source=source,
    )


class GreenhouseAdapter(JobSourceAdapter):
    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        company = filters.get("company", "")
        if not company:
            return []
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
                )
                resp.raise_for_status()
                data = resp.json()
            jobs: list[Job] = []
            for item in data.get("jobs", []):
                jobs.append(
                    _to_job(
                        source="greenhouse",
                        job_id=str(item.get("id", "")),
                        title=item.get("title", ""),
                        company=item.get("company", {}).get("name", company),
                        description=item.get("content", "") or "",
                        location=item.get("location", {}).get("name"),
                        url=item.get("absolute_url"),
                    )
                )
            return jobs
        except Exception:
            return []


class LeverAdapter(JobSourceAdapter):
    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        company = filters.get("company", "")
        if not company:
            return []
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"https://api.lever.co/v0/postings/{company}",
                    params={"mode": "json"},
                )
                resp.raise_for_status()
                data = resp.json()
            jobs: list[Job] = []
            for item in data:
                jobs.append(
                    _to_job(
                        source="lever",
                        job_id=str(item.get("id", "")),
                        title=item.get("text", ""),
                        company=company,
                        description=item.get("descriptionPlain", "") or "",
                        location=(item.get("categories") or {}).get("location"),
                        url=item.get("applyUrl") or item.get("hostedUrl"),
                    )
                )
            return jobs
        except Exception:
            return []


class AshbyAdapter(JobSourceAdapter):
    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        company = filters.get("company", "")
        if not company:
            return []
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    "https://api.ashbyhq.com/1.0/job-board/list",
                    json={"company": company},
                )
                resp.raise_for_status()
                data = resp.json()
            jobs: list[Job] = []
            for item in data.get("jobs", []):
                jobs.append(
                    _to_job(
                        source="ashby",
                        job_id=str(item.get("id", "")),
                        title=item.get("title", ""),
                        company=company,
                        description=item.get("description", "") or "",
                        location=item.get("location"),
                        url=item.get("url"),
                    )
                )
            return jobs
        except Exception:
            return []


class AdzunaAdapter(JobSourceAdapter):
    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        if not settings.enable_adzuna or not settings.adzuna_app_id or not settings.adzuna_app_key:
            return []
        query = filters.get("query", "")
        location = filters.get("location", "us")
        page = filters.get("page", 1)
        per_page = filters.get("limit", 20)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"https://api.adzuna.com/v1/api/jobs/{location}/{page}",
                    params={
                        "app_id": settings.adzuna_app_id,
                        "app_key": settings.adzuna_app_key,
                        "results_per_page": per_page,
                        "what": query,
                        "content-type": "application/json",
                    },
                )
                resp.raise_for_status()
                data = resp.json()
            jobs: list[Job] = []
            for item in data.get("results", []):
                jobs.append(
                    _to_job(
                        source="adzuna",
                        job_id=str(item.get("id", "")),
                        title=item.get("title", ""),
                        company=(item.get("company") or {}).get("display_name", ""),
                        description=item.get("description", "") or "",
                        location=(item.get("location") or {}).get("display_name"),
                        url=item.get("redirect_url"),
                        requirements=item.get("tags", [])
                        if isinstance(item.get("tags"), list)
                        else [],
                    )
                )
            return jobs
        except Exception:
            return []


class RemoteOKAdapter(JobSourceAdapter):
    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        if not settings.enable_remoteok:
            return []
        query = filters.get("query", "")
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get("https://remoteok.com/api")
                resp.raise_for_status()
                data = resp.json()
            jobs: list[Job] = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                if item.get("type") != "job":
                    continue
                tags = item.get("tags") or []
                if (
                    query
                    and query.lower() not in " ".join(tags).lower()
                    and query.lower() not in item.get("position", "").lower()
                ):
                    continue
                jobs.append(
                    _to_job(
                        source="remoteok",
                        job_id=str(item.get("id", "")),
                        title=item.get("position", ""),
                        company=item.get("company", ""),
                        description=item.get("description", "") or "",
                        location=item.get("location"),
                        url=item.get("url") or item.get("apply_url"),
                        requirements=tags,
                    )
                )
            return jobs
        except Exception:
            return []


class CustomCareerPageAdapter(JobSourceAdapter):
    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        url = filters.get("url", "")
        if not url:
            return []
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(url)
                resp.raise_for_status()
            # Minimal fallback: extract nothing actionable; caller should parse
            return []
        except Exception:
            return []


ADAPTERS = {
    "greenhouse": GreenhouseAdapter(),
    "lever": LeverAdapter(),
    "ashby": AshbyAdapter(),
    "adzuna": AdzunaAdapter(),
    "remoteok": RemoteOKAdapter(),
    "custom": CustomCareerPageAdapter(),
}
