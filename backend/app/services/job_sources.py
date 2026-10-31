from typing import Any

import httpx

from ..models.schemas import Job


class RemoteOKAdapter:
    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        try:
            async with httpx.AsyncClient(
                timeout=30.0, headers={"User-Agent": "HireLoop"}
            ) as client:
                resp = await client.get("https://remoteok.io/api")
                if resp.status_code != 200:
                    return []
                data = resp.json()
                jobs = []
                for item in data[1:100]:
                    if not isinstance(item, dict):
                        continue
                    job = Job(
                        id=f"rok_{item.get('id', '')}",
                        title=item.get("position", "Unknown"),
                        company=item.get("company", "Unknown"),
                        location=item.get("location", "Remote"),
                        description=str(item.get("description", ""))[:500],
                        requirements=item.get("tags", [])[:10]
                        if isinstance(item.get("tags"), list)
                        else [],
                        url=item.get(
                            "url", f"https://remoteok.io/remote-jobs/{item.get('slug', '')}"
                        ),
                        source="remoteok",
                    )
                    jobs.append(job)
                return jobs
        except Exception:
            return []


class WeWorkRemotelyAdapter:
    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get("https://weworkremotely.com/categories/remote-jobs.json")
                if resp.status_code != 200:
                    return []
                data = resp.json()
                jobs = []
                for item in data[:50] if isinstance(data, list) else []:
                    if not isinstance(item, dict):
                        continue
                    job = Job(
                        id=f"wwr_{item.get('id', '')}",
                        title=item.get("title", "Unknown"),
                        company=item.get("company", {}).get("name", "Unknown")
                        if isinstance(item.get("company"), dict)
                        else item.get("company", "Unknown"),
                        location="Remote",
                        description=str(item.get("description", ""))[:500],
                        requirements=[],
                        url=item.get("url", ""),
                        source="weworkremotely",
                    )
                    jobs.append(job)
                return jobs
        except Exception:
            return []


class JobicyAdapter:
    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get("https://jobicy.com/api/v2/remote-jobs?count=50")
                if resp.status_code != 200:
                    return []
                data = resp.json()
                jobs = []
                for item in data.get("jobs", [])[:50]:
                    if not isinstance(item, dict):
                        continue
                    job = Job(
                        id=f"jcy_{item.get('jobId', '')}",
                        title=item.get("jobTitle", "Unknown"),
                        company=item.get("companyName", "Unknown"),
                        location=item.get("jobGeo", "Remote"),
                        description=str(item.get("jobDescription", ""))[:500],
                        requirements=item.get("jobTags", [])[:10]
                        if isinstance(item.get("jobTags"), list)
                        else [],
                        url=item.get("url", ""),
                        source="jobicy",
                    )
                    jobs.append(job)
                return jobs
        except Exception:
            return []


class GreenhouseAdapter:
    """Public Greenhouse ATS board API. Requires company slugs in filters['companies']."""

    def __init__(self):
        self._default_companies = [
            "stripe",
            "airbnb",
            "shopify",
            "github",
            "twitch",
            "dropbox",
            "instacart",
            "reddit",
            "lyft",
            "square",
        ]

    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        companies = filters.get("companies") or self._default_companies
        jobs: list[Job] = []
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                for company in companies[:10]:
                    try:
                        resp = await client.get(
                            f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
                        )
                        if resp.status_code != 200:
                            continue
                        data = resp.json()
                        for item in data.get("jobs", [])[:20]:
                            job = Job(
                                id=f"gh_{item.get('id', '')}",
                                title=item.get("title", "Unknown"),
                                company=company.title(),
                                location=item.get("location", {}).get("name", "Remote"),
                                description=str(item.get("content", ""))[:500],
                                requirements=[],
                                url=item.get("absolute_url", ""),
                                source="greenhouse",
                            )
                            jobs.append(job)
                    except Exception:
                        continue
        except Exception:
            pass
        return jobs


class LeverAdapter:
    """Public Lever ATS posting API. Requires company slugs in filters['companies']."""

    def __init__(self):
        self._default_companies = [
            "netflix",
            "spotify",
            "figma",
            "notion",
            "linear",
            "replit",
            "vercel",
            "anthropic",
            "openai",
            "scale",
        ]

    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        companies = filters.get("companies") or self._default_companies
        jobs: list[Job] = []
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                for company in companies[:10]:
                    try:
                        resp = await client.get(
                            f"https://api.lever.co/v0/postings/{company}?mode=json"
                        )
                        if resp.status_code != 200:
                            continue
                        data = resp.json()
                        for item in data[:20]:
                            if not isinstance(item, dict):
                                continue
                            job = Job(
                                id=f"lv_{item.get('id', '')}",
                                title=item.get("text", "Unknown"),
                                company=company.title(),
                                location=(
                                    item.get("categories", {}).get("location", "Remote")
                                    if isinstance(item.get("categories"), dict)
                                    else "Remote"
                                ),
                                description=str(item.get("descriptionPlain", ""))[:500],
                                requirements=[],
                                url=item.get("applyUrl", ""),
                                source="lever",
                            )
                            jobs.append(job)
                    except Exception:
                        continue
        except Exception:
            pass
        return jobs


class AshbyAdapter:
    """Public Ashby ATS posting API. Requires company slugs in filters['companies']."""

    def __init__(self):
        self._default_companies = [
            "linear",
            "replit",
            "vercel",
            "anthropic",
            "openai",
            "scale",
            "perplexity",
            "cohere",
        ]

    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        companies = filters.get("companies") or self._default_companies
        jobs: list[Job] = []
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                for company in companies[:10]:
                    try:
                        resp = await client.get(
                            f"https://apply.ashbyhq.com/api/1.0/jobs/postings?organization={company}"
                        )
                        if resp.status_code != 200:
                            continue
                        data = resp.json()
                        for item in data.get("results", [])[:20]:
                            if not isinstance(item, dict):
                                continue
                            job = Job(
                                id=f"ash_{item.get('id', '')}",
                                title=item.get("title", "Unknown"),
                                company=company.title(),
                                location="Remote",
                                description=str(item.get("description", ""))[:500],
                                requirements=[],
                                url=item.get("applicationUrl", ""),
                                source="ashby",
                            )
                            jobs.append(job)
                    except Exception:
                        continue
        except Exception:
            pass
        return jobs


class AdzunaAdapter:
    """Adzuna public job search API. Requires ADZUNA_APP_ID and ADZUNA_APP_KEY in env."""

    def __init__(self):
        from app.core.config import get_settings

        settings = get_settings()
        self.app_id = settings.adzuna_app_id
        self.app_key = settings.adzuna_app_key

    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        if not self.app_id or not self.app_key:
            return []
        country = filters.get("country", "us")
        query = filters.get("query", "software engineer")
        jobs: list[Job] = []
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(
                    f"https://api.adzuna.com/v1/api/jobs/{country}/search/1",
                    params={
                        "app_id": self.app_id,
                        "app_key": self.app_key,
                        "results_per_page": 30,
                        "what": query,
                        "content-type": "application/json",
                    },
                )
                if resp.status_code != 200:
                    return []
                data = resp.json()
                for item in data.get("results", [])[:30]:
                    if not isinstance(item, dict):
                        continue
                    job = Job(
                        id=f"adz_{item.get('id', '')}",
                        title=item.get("title", "Unknown"),
                        company=item.get("company", {}).get("display_name", "Unknown"),
                        location=item.get("location", {}).get("display_name", "Remote"),
                        description=str(item.get("description", ""))[:500],
                        requirements=[],
                        url=item.get("redirect_url", ""),
                        source="adzuna",
                    )
                    jobs.append(job)
        except Exception:
            pass
        return jobs


class OttaAdapter:
    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        return []


class HimalayasAdapter:
    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get("https://himalayas.app/jobs/api")
                if resp.status_code != 200:
                    return []
                data = resp.json()
                jobs = []
                for item in data[:50] if isinstance(data, list) else []:
                    if not isinstance(item, dict):
                        continue
                    job = Job(
                        id=f"him_{item.get('id', '')}",
                        title=item.get("title", "Unknown"),
                        company=item.get("companyName", "Unknown"),
                        location=item.get("locationRestrictions", ["Remote"])[0]
                        if isinstance(item.get("locationRestrictions"), list)
                        and item.get("locationRestrictions")
                        else "Remote",
                        description=str(item.get("description", ""))[:500],
                        requirements=item.get("skills", [])[:10]
                        if isinstance(item.get("skills"), list)
                        else [],
                        url=item.get("applicationLink", "") or item.get("url", ""),
                        source="himalayas",
                    )
                    jobs.append(job)
                return jobs
        except Exception:
            return []


ADAPTERS: dict[str, Any] = {
    "remoteok": RemoteOKAdapter(),
    "weworkremotely": WeWorkRemotelyAdapter(),
    "jobicy": JobicyAdapter(),
    "greenhouse": GreenhouseAdapter(),
    "lever": LeverAdapter(),
    "ashby": AshbyAdapter(),
    "adzuna": AdzunaAdapter(),
    "himalayas": HimalayasAdapter(),
    "otta": OttaAdapter(),
}
