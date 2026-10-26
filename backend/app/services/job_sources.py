import httpx
from typing import Any

from ..models.schemas import Job


class RemoteOKAdapter:
    async def fetch(self, filters: dict[str, Any]) -> list[Job]:
        try:
            async with httpx.AsyncClient(timeout=30.0, headers={"User-Agent": "HireLoop"}) as client:
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
                        requirements=item.get("tags", [])[:10] if isinstance(item.get("tags"), list) else [],
                        url=item.get("url", f"https://remoteok.io/remote-jobs/{item.get('slug', '')}"),
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
                        company=item.get("company", {}).get("name", "Unknown") if isinstance(item.get("company"), dict) else item.get("company", "Unknown"),
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
                        requirements=item.get("jobTags", [])[:10] if isinstance(item.get("jobTags"), list) else [],
                        url=item.get("url", ""),
                        source="jobicy",
                    )
                    jobs.append(job)
                return jobs
        except Exception:
            return []


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
                        location=item.get("locationRestrictions", ["Remote"])[0] if isinstance(item.get("locationRestrictions"), list) and item.get("locationRestrictions") else "Remote",
                        description=str(item.get("description", ""))[:500],
                        requirements=item.get("skills", [])[:10] if isinstance(item.get("skills"), list) else [],
                        url=item.get("applicationLink", "") or item.get("url", ""),
                        source="himalayas",
                    )
                    jobs.append(job)
                return jobs
        except Exception:
            return []


ADAPTERS = {
    "remoteok": RemoteOKAdapter(),
    "weworkremotely": WeWorkRemotelyAdapter(),
    "jobicy": JobicyAdapter(),
    "himalayas": HimalayasAdapter(),
}
